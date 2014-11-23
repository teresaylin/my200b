var module = angular.module('repositories', []);

module.factory('CommentRepository', function($http) {
    var baseUrl = '/api/comments/';
    
    return {
        get: function(id) {
            return $http.get(baseUrl+id+'/');
        },
        list: function(params) {
            return $http.get(baseUrl, { params: params });
        },
        create: function(data) {
            return $http.post(baseUrl, data);
        }
    };
});

module.factory('EventRepository', function($http) {
    var baseUrl = '/api/events/';
    
    return {
        get: function(id) {
            return $http.get(baseUrl+id+'/');
        },
        list: function(params) {
            return $http.get(baseUrl, { params: params });
        },
        create: function(data) {
            return $http.post(baseUrl, data);
        },
        update: function(id, data) {
            return $http.put(baseUrl+id+'/', data);
        },
        delete: function(id) {
            return $http.delete(baseUrl+id+'/');
        },
        addAttendee: function(id, userId) {
            return $http.put(baseUrl+id+'/add_attendee/', {
                'user_id': userId
            });
        },
        addAttendeeTaskforce: function(id, taskforceId) {
            return $http.put(baseUrl+id+'/add_attendee_taskforce/', {
                'taskforce_id': taskforceId
            });
        },
        removeAttendee: function(id, userId) {
            return $http.put(baseUrl+id+'/remove_attendee/', {
                'user_id': userId
            });
        },
        addFile: function(id, path) {
            return $http.put(baseUrl+id+'/add_file/', {
                'path': path
            });
        },
        removeFile: function(id, path) {
            return $http.put(baseUrl+id+'/remove_file/', {
                'path': path
            });
        }
    };
});

module.factory('MilestoneRepository', function($http) {
    var baseUrl = '/api/milestones/';
    
    return {
        get: function(id) {
            return $http.get(baseUrl+id+'/');
        },
        list: function(params) {
            return $http.get(baseUrl, { params: params });
        }
    };
});

module.factory('RoleRepository', function($http) {
    var baseUrl = '/api/roles/';
    
    return {
        get: function(id) {
            return $http.get(baseUrl+id+'/');
        },
        list: function(params) {
            return $http.get(baseUrl, { params: params });
        }
    };
});

module.factory('TaskRepository', function($http) {
    var baseUrl = '/api/tasks/';
    
    return {
        get: function(id) {
            return $http.get(baseUrl+id+'/');
        },
        list: function(params) {
            return $http.get(baseUrl, { params: params });
        },
        create: function(data) {
            return $http.post(baseUrl, data);
        },
        update: function(id, data) {
            return $http.put(baseUrl+id+'/', data);
        },
        delete: function(id) {
            return $http.delete(baseUrl+id+'/');
        },
        complete: function(id) {
            return $http.put(baseUrl+id+'/complete/');
        },
        addAssignedUser: function(id, userId) {
            return $http.put(baseUrl+id+'/add_assigned_user/', {
                'user_id': userId
            });
        },
        removeAssignedUser: function(id, userId) {
            return $http.put(baseUrl+id+'/remove_assigned_user/', {
                'user_id': userId
            });
        },
        addAssignedTaskforce: function(id, taskforceId) {
            return $http.put(baseUrl+id+'/add_assigned_taskforce/', {
                'taskforce_id': taskforceId
            });
        },
        removeAssignedTaskforce: function(id, taskforceId) {
            return $http.put(baseUrl+id+'/remove_assigned_taskforce/', {
                'taskforce_id': taskforceId
            });
        },
        addFile: function(id, path) {
            return $http.put(baseUrl+id+'/add_file/', {
                'path': path
            });
        },
        removeFile: function(id, path) {
            return $http.put(baseUrl+id+'/remove_file/', {
                'path': path
            });
        }
    };
});

module.factory('TaskForceRepository', function($http) {
    var baseUrl = '/api/taskforces/';
    
    return {
        get: function(id) {
            return $http.get(baseUrl+id+'/');
        },
        list: function(params) {
            return $http.get(baseUrl, { params: params });
        },
        create: function(data) {
            return $http.post(baseUrl, data);
        },
        update: function(id, data) {
            return $http.put(baseUrl+id+'/', data);
        },
        delete: function(id) {
            return $http.delete(baseUrl+id+'/');
        },
        addMember: function(id, userId) {
            return $http.put(baseUrl+id+'/add_member/', {
                'user_id': userId
            });
        },
        removeMember: function(id, userId) {
            return $http.put(baseUrl+id+'/remove_member/', {
                'user_id': userId
            });
        }
    };
});

module.factory('TeamRepository', function($http) {
    var baseUrl = '/api/teams/';
    
    return {
        get: function(id) {
            return $http.get(baseUrl+id+'/');
        },
        list: function(params) {
            return $http.get(baseUrl, { params: params });
        }
    };
});

module.factory('UserRepository', function($http) {
    var baseUrl = '/api/users/';
    var profilesUrl = '/api/user-profiles/';
    
    return {
        get: function(id) {
            return $http.get(baseUrl+id+'/');
        },
        getCurrentUser: function() {
            return $http.get(baseUrl+'?current');
        },
        list: function(params) {
            return $http.get(baseUrl, { params: params });
        },
        updateProfile: function(id, data) {
            return $http.put(profilesUrl+id+'/', data);
        },
        addRole: function(id, roleId) {
            return $http.put(baseUrl+id+'/add_role/', {
                'role_id': roleId
            });
        },
        removeRole: function(id, roleId) {
            return $http.put(baseUrl+id+'/remove_role/', {
                'role_id': roleId
            });
        }
    };
});