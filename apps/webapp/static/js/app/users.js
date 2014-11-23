var module = angular.module('users', []);

module.controller('UserDetailStateCtrl', function($scope, $stateParams, $modal, UserRepository, RoleRepository) {
    // Get user
    UserRepository.get($stateParams.userId)
        .success(function(user) {
            $scope.user = user;
        });
        
    // Get list of roles that user can assign themselves when viewing own profile
    $scope.$watch('currentUser', function(currentUser) {
        if(currentUser && currentUser.id == $stateParams.userId) {
            RoleRepository.list({ 'user_assignable': true })
                .success(function(roles) {
                    $scope.roles = roles;
                });
        }
    });
        
    $scope.openEditProfileDialog = function() {
        var modal = $modal.open({
            backdrop: 'static',
            templateUrl: partial('users/edit-profile-dialog.html'),
            controller: function($scope, $modalInstance, user) {
                if(user.profile) {
                    // Copy existing profile
                    $scope.profile = angular.copy(user.profile);
                } else {
                    // Create new profile
                    $scope.profile = {};
                }
                
                $scope.ok = function(form) {
                    // Update profile
                    UserRepository.updateProfile(user.id, $scope.profile)
                        .success(function() {
                            $modalInstance.close($scope.profile);
                        });
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
            },
            resolve: {
                user: function() {
                    return $scope.user;
                }
            }
        });
        
        modal.result.then(function(profile) {
            // Add updated profile to user object
            $scope.user.profile = profile;
        });
    };

    $scope.addRole = function(role) {
        UserRepository.addRole($scope.user.id, role.id)
            .success(function(userRole) {
                $scope.user.user_roles.push(userRole);
            });
    };
    
    $scope.removeRole = function(userRole) {
        UserRepository.removeRole($scope.user.id, userRole.role.id)
            .success(function() {
                var a = $scope.user.user_roles;
                a.splice(a.indexOf(userRole), 1);
            });
    };
});

module.controller('TeamStateCtrl', function($scope, $rootScope, $modal, NavFilterService, TeamRepository, UserRepository, TaskForceRepository) {
    var update = function() {
        if(NavFilterService.team) {
            $scope.team = NavFilterService.team;

            // Get list of users in selected team
            UserRepository.list({ teams: NavFilterService.team.id })
                .success(function(users) {
                    $scope.users = users;
                });
            
            // Get root task forces
            TaskForceRepository.list({
                team: NavFilterService.team.id,
                root: true
            })
                .success(function(data) {
                    $scope.taskForces = data;
                });
        }
    };
    
    // Called when user opens a task force in the accordion
    $scope.getTaskForceChildren = function(taskForce) {
        // Get taskForce children if they don't exist
        if(!('children' in taskForce)) {
            TaskForceRepository.get(taskForce.id)
                .success(function(data) {
                    taskForce.children = data.children;
                });
        }
    };
    
    // Create/update a task force
    $scope.openEditTaskForceDialog = function(taskforce, parent) {
        var modal = $modal.open({
            backdrop: 'static',
            templateUrl: partial('team/edit-taskforce-dialog.html'),
            controller: function($scope, $modalInstance, TaskForceRepository, MilestoneRepository, team) {
                $scope.hasParent = parent ? true : false;
                
                if(taskforce) {
                    // Editing existing taskforce
                    $scope.creating = false;
                    $scope.taskforce = angular.copy(taskforce);
                } else {
                    // Creating new taskforce
                    $scope.creating = true;
                    $scope.taskforce = {
                        milestone: parent ? parent.milestone : null,
                        team: team.id,
                        parent_task_force: parent ? parent.id : null
                    };
                }
                
                // Get list of all milestones
                MilestoneRepository.list()
                    .success(function(data) {
                        $scope.milestones = data;
                        
                        // Angular <select> detects the default selection by reference,
                        // so replace the existing milestone object with the copy in the list.
                        if($scope.taskforce.milestone) {
                            angular.forEach(data, function(milestone) {
                                if($scope.taskforce.milestone.id == milestone.id) {
                                    $scope.taskforce.milestone = milestone;
                                }
                            });
                        }
                    });
                
                $scope.create = function(form) {
                    // Create task force
                    $scope.taskforce.milestone_id = $scope.taskforce.milestone.id;
                    TaskForceRepository.create($scope.taskforce)
                        .success(function(data) {
                            $rootScope.$broadcast('taskforceCreated', data);
                            $modalInstance.close();
                        });
                };
                
                $scope.update = function(form) {
                    // Update task force
                    $scope.taskforce.milestone_id = $scope.taskforce.milestone.id;
                    TaskForceRepository.update($scope.taskforce.id, $scope.taskforce)
                        .success(function() {
                            // Overwrite original object with updated object
                            angular.copy($scope.taskforce, taskforce);
                            $modalInstance.close();
                        });
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
            },
            resolve: {
                team: function() {
                    return $scope.team;
                }
            }
        });
        
        modal.result.then(function() {
            // If creating a new object
            if(!taskforce) {
                if(parent) {
                    // Refresh parent task force's children
                    TaskForceRepository.get(parent.id)
                        .success(function(data) {
                            parent.children = data.children;
                        });
                } else {
                    // No parent, refresh root task force list
                    update();
                }
            }
        });
    };
    
    // Delete task force
    $scope.openDeleteTaskForceDialog = function(taskforce) {
        var modal = $modal.open({
            backdrop: 'static',
            templateUrl: partial('team/delete-taskforce-dialog.html'),
            controller: function($scope, $modalInstance, TaskForceRepository) {
                $scope.taskforce = taskforce;
                
                $scope.delete = function(form) {
                    // Delete task force
                    TaskForceRepository.delete(taskforce.id)
                        .success(function() {
                            $rootScope.$broadcast('taskforceDeleted', taskforce);
                            $modalInstance.close();
                        });
                };

                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
            }
        });
        
        modal.result.then(function() {
            var deletedId = taskforce.id;
            
            // Recursively scan task force tree and remove the deleted task force (urgh...)
            var scan = function(taskforces) {
                angular.forEach(taskforces, function(taskforce, idx) {
                    if(taskforce.id == deletedId) {
                        taskforces.splice(idx, 1);
                        return;
                    }
                    
                    if('children' in taskforce) {
                        scan(taskforce.children);
                    }
                });
            };
            scan($scope.taskForces);
        });
    };
    
    $scope.addTaskForceMember = function(taskforce, user) {
        TaskForceRepository.addMember(taskforce.id, user.id)
            .success(function() {
                taskforce.members.push(user);
            });
    };

    $scope.removeTaskForceMember = function(taskforce, user) {
        TaskForceRepository.removeMember(taskforce.id, user.id)
            .success(function() {
                taskforce.members.splice(taskforce.members.indexOf(user), 1);
            });
    };

    // Update when team changes
    $scope.$on('navFilterChanged', function(event, changed) {
        if('team' in changed) {
            update();
        }
    });

    // Get users
    update();
});

module.directive('userPicture', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            scope.$watch(attrs.userPicture, function(user) {
                if(user) {
                    var size = attrs.size;
                    if('profile' in user && user.profile && user.profile.picture_filename) {
                        var imgFile = user.profile.picture_filename+'.jpg';
                    } else {
                        var imgFile = '_unavailable.png';
                    }
                    var imgPath = '/static/img/profile-photos/'+size+'/'+imgFile;
                    element.attr('src', imgPath);
                }
            });
        }
    };
});

module.directive('userPicker', function(NavFilterService, UserRepository) {
    return {
        restrict: 'E',
        scope: {
            user: '=',
            restrictTeam: '='
        },
        templateUrl: 'components/user-picker.html',
        link: function(scope, element, attrs) {
            scope.search = function(q) {
                var params = {
                    search_name: q,
                    page_size: 10,
                };
                if(scope.restrictTeam) {
                    params.teams = scope.restrictTeam.id;
                } else {
                    // Restrict to team selected in nav filter, by default
                    if(NavFilterService.team) {
                        params.teams = NavFilterService.team.id;
                    }
                }

                return UserRepository.list(params)
                    .then(function(res){
                        return res.data.results;
                    });
            };
        }
    };
});

module.directive('taskforcePicker', function(TaskForceRepository, NavFilterService) {
    return {
        restrict: 'E',
        scope: {
            taskforce: '='
        },
        templateUrl: 'components/taskforce-picker.html',
        link: function(scope, element, attrs) {
            scope.search = function(q) {
                if(NavFilterService.team) {
                    return TaskForceRepository.list({
                        search_name: q,
                        page_size: 10,
                        team: NavFilterService.team.id // Restrict taskforce search to currently active team
                    })
                        .then(function(res){
                            return res.data.results;
                        });
                }
            };
        }
    };
});

module.directive('commentsSection', function($http, CommentRepository) {
    return {
        restrict: 'E',
        scope: {
        },
        templateUrl: 'components/comments-section.html',
        link: function(scope, element, attrs) {
            var threadId = null;

            scope.nextPageUrl = null;
            
            scope.$parent.$watch(attrs.threadId, function(val) {
                if(val) {
                    threadId = val;

                    // Get most recent comments
                    CommentRepository.list({
                        'thread': threadId,
                        'page_size': 10
                    })
                        .success(function(data) {
                            scope.comments = data.results;
                            scope.nextPageUrl = data.next;
                        });
                }
            });
            
            // Load older comments
            scope.more = function() {
                if(!scope.nextPageUrl) return;
                
                // Retrieve next page of comments and add to scope.comments
                $http.get(scope.nextPageUrl)
                    .success(function(data) {
                        Array.prototype.push.apply(scope.comments, data.results);
                        scope.nextPageUrl = data.next;
                    });
            };
            
            // Post comment from this user 
            scope.postComment = function(body) {
                var comment = {
                    'thread': threadId,
                    'body': body
                };

                CommentRepository.create(comment)
                    .success(function(newComment) {
                        scope.comments.unshift(newComment);
                    });
            };
        }
    };
});
