var module = angular.module('files', [
    'ngCookies',
    'angularFileUpload'
]);

// 'filename' directive
module.directive('filename', function() {
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            ctrl.$parsers.unshift(function(viewValue) {
                if(/[\[\]\/\\=+<>:;",*]/.test(viewValue)) {
                    // Invalid filename
                    ctrl.$setValidity('filename', false);
                    return undefined;
                } else {
                    // Valid filename
                    ctrl.$setValidity('filename', true);
                    return viewValue;
                }
            });
        }
    };
});

// 'basename' filter: get filename from full path
module.filter('basename', function() {
    return function(path) {
        return path.substr(path.lastIndexOf('/') + 1);
    };
});

// 'filesize' filter: get human-friendly file size
module.filter('filesize', function() {
    return function(sizeBytes) {
        if(sizeBytes >= 1024*1024*1024) {
            return (sizeBytes / (1024*1024*1024)).toFixed(1) + ' GB';
        } else if(sizeBytes >= 1024*1024) {
            return (sizeBytes / (1024*1024)).toFixed(1) + ' MB';
        } else if(sizeBytes >= 1024) {
            return (sizeBytes / 1024).toFixed(1) + ' KB';
        } else {
            return sizeBytes + ' bytes';
        }
    };
});

// This directive allows a button to trigger an invisible file <input>
module.directive('fileInputContainer', function() {
    return {
        restrict: 'E',
        scope: {},
        link: function(scope, elm, attrs) {
            var input = elm.find('input[type="file"]');
            input.css('display', 'none');
            elm.find('button').click(function() {
                input.click();
            });
        }
    };
});

module.directive('pathBreadcrumbs', function() {
    return {
        restrict: 'E',
        scope: {
            pathChange: '&'
        },
        templateUrl: 'components/path-breadcrumbs.html',
        link: function(scope, elm, attrs) {
            scope.$parent.$watch(attrs.path, function(path) {
                if(path) {
                    var fragments = path.split('/');
                    
                    // Remove empty fragments caused by leading and trailing slashes
                    if(fragments.length > 0 && fragments[0] == '') {
                        fragments.shift();
                    }
                    if(fragments.length > 0 && fragments[fragments.length-1] == '') {
                        fragments.pop();
                    }

                    scope.fragments = fragments;
                }
            });
            
            scope.fragmentClicked = function(idx) {
                var path = scope.fragments.slice(0, idx+1);
                path = '/' + path.join('/');
                scope.pathChange({ path: path });
            };
        }
    };
});

module.directive('fileThumbnail', function(FileRepository) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            // As the Dropbox 48x48 icon set is incomplete, we need to map replacement icon filenames
            var iconMap = {
                'page_white_excel': 'excel',
                'page_white_film': 'page_white_dvd',
                'page_white_powerpoint': 'powerpoint',
                'page_white_word': 'word',
                'page_white_sound': 'music',
                'page_white_compressed': 'page_white_zip'
            };

            scope.$watch(attrs.fileThumbnail, function(file) {
                if(file) {
                    var size = attrs.size;
                    
                    if(file.thumb_exists) {
                        var imgPath = FileRepository.getThumbnailUrl(file.path, size);
                    } else {
                        if(file.icon in iconMap) {
                            var filename = iconMap[file.icon];
                        } else {
                            var filename = file.icon;
                        }
                        var imgPath = '/static/img/dropbox/icons/48x48/'+filename+'48.gif';
                    }
                    element.attr('src', imgPath);
                }
            });
        }
    };
});

module.directive('filePicker', function(FileRepository, NavFilterService) {
    return {
        restrict: 'E',
        scope: {
            'file': '='
        },
        templateUrl: 'components/file-picker.html',
        link: function(scope, element, attrs) {
            scope.search = function(q) {
                if(NavFilterService.team) {
                    return FileRepository.search('/'+NavFilterService.team.color, q)
                        .then(function(res) {
                            return res.data;
                        });
                }
            };
        }
    };
});

module.factory('FileRepository', function($http) {
    var baseUrl = '/api/files/';
    
    //! Adds 'name' and 'dir_path' field to a file object
    var injectFilenames = function(file) {
        var dirname = function(path) {
            var i = path.lastIndexOf('/');
            return i > 0 ? path.substr(0, i) : i;
        };

        var basename = function(path) {
            return path.substr(path.lastIndexOf('/') + 1);
        };
        
        file.name = basename(file.path);
        file.dir_path = dirname(file.path);
        if('contents' in file) {
            angular.forEach(file.contents, function(childFile) {
                childFile.name = basename(childFile.path);
                childFile.dir_path = dirname(childFile.path);
            });
        }
    };
    
    return {
        injectFilenames: injectFilenames,
        metadata: function(path) {
            return $http.get(baseUrl+'metadata'+path)
                .success(function(data) {
                    injectFilenames(data);
                });
        },
        search: function(path, query) {
            return $http.get(baseUrl+'search'+path, { params: {
                query: query
            }});
        },
        delete: function(paths) {
            return $http.post(baseUrl+'delete/', {
                'paths': paths
            });
        },
        createFolder: function(path) {
            return $http.post(baseUrl+'create-folder/', {
                'path': path
            })
                .success(function(data) {
                    injectFilenames(data);
                });
        },
        getThumbnailUrl: function(path, size) {
            return baseUrl+'thumbnails'+path+'/'+size+'.jpeg';
        },
        getPreviewUrl: function(path, size) {
            return baseUrl+'previews'+path;
        },
        getUploadUrl: function() {
            return baseUrl+'upload/';
        }
        /*
        getFileShare: function(id) {
            return $http.get(baseUrl+id+'/share/');
        }
        */
    };
});

module.controller('FileBrowserCtrl', function($scope, $modal, NavFilterService, FileRepository, FileDialogService) {
    // Change to team's root directory when nav filter team changes
    $scope.$on('navFilterChanged', function(event, changed) {
        if('team' in changed) {
            $scope.setDirectory('/'+NavFilterService.team.color);
        }
    });
    
    $scope.fileOrder = [
        '-is_dir',
        'name'
    ];
    
    $scope.refresh = function() {
        // Retrieve metadata
        FileRepository.metadata($scope.directory.path)
            .success(function(data) {
                $scope.directory = data;
                $scope.clearSelection();
            });
    };

    $scope.setDirectory = function(path) {
        // Retrieve metadata
        FileRepository.metadata(path)
            .success(function(data) {
                $scope.directory = data;
                $scope.clearSelection();
            });
    };
    
    // Add newly created files to the directory contents
    $scope.$on('fileCreated', function(event, file) {
        if(file.dir_path == $scope.directory.path) {
            $scope.directory.contents.push(file);
        }
    });

    // Update directory contents on 'fileUpdated' event
    $scope.$on('fileUpdated', function(event, file) {
        if(file.dir_path == $scope.directory.path) {
            angular.forEach($scope.directory.contents, function(dirFile) {
                if(dirFile.path == file.path) {
                    angular.copy(file, dirFile);
                }
            });
        }
    });
    
    // Remove files from directory on 'fileDeleted' event
    $scope.$on('fileDeleted', function(event, file) {
        if(file.dir_path == $scope.directory.path) {
            angular.forEach($scope.directory.contents, function(dirFile, i) {
                if(dirFile.path == file.path) {
                    $scope.directory.contents.splice(i, 1);
                }
            });
            
            // Clear the deleted file from the selection
            if(file.path in $scope.selection) {
                delete $scope.selection[file.path];
                $scope.selectionLength = Object.keys($scope.selection).length;
            }
        }
    });
        
    // Called when user clicks a file/directory
    $scope.openFile = function(file) {
        if(file.is_dir) {
            $scope.setDirectory(file.path);
        } else {
            FileDialogService.openFile(file);
        }
    };
    
    $scope.selection = {};
    $scope.selectionLength = 0;
    $scope.selectFile = function(file, toggle) {
        if(toggle) {
            var selected = !(file.path in $scope.selection);
        } else {
            var selected = true;
        }
        
        if(selected) {
            if(!toggle) $scope.selection = {};
            $scope.selection[file.path] = file;
        } else {
            delete $scope.selection[file.path];
        }
        
        $scope.selectionLength = Object.keys($scope.selection).length;
    };
    
    $scope.clearSelection = function() {
        $scope.selection = {};
        $scope.selectionLength = 0;
    };
    
    $scope.deleteSelection = function() {
        // Convert selection to array of files
        var files = [];
        angular.forEach($scope.selection, function(v) {
            files.push(v);
        });
        
        // Delete
        FileDialogService.deleteFiles(files);
    };
    
    var MAX_UPLOAD_SIZE = 50*1024*1024;
    var showUploadSizeLimitDialog = function() {
        var modal = $modal.open({
            backdrop: 'static',
            templateUrl: partial('files/upload-size-limit-dialog.html'),
            controller: function($scope, $modalInstance) {
                $scope.maxSize = MAX_UPLOAD_SIZE;
                
                $scope.close = function() {
                    $modalInstance.close();
                };
            }
        });
                
        return modal;
    };
    
    $scope.openUploadDialog = function() {
        if(!$scope.directory) return;

        var modal = $modal.open({
            backdrop: 'static',
            templateUrl: partial('files/upload-dialog.html'),
            controller: function($scope, $rootScope, $modalInstance, $cookies, FileUploader, FileRepository, directory) {
                $scope.directory = directory;
                
                $scope.uploader = new FileUploader({
                    url: FileRepository.getUploadUrl(),
                    headers: {
                        'X-CSRFToken': $cookies.csrftoken
                    },
                    autoUpload: true,
                    filters: [{
                        name: 'sizeLimit',
                        fn: function(file) {
                            if(file.size > MAX_UPLOAD_SIZE) {
                                showUploadSizeLimitDialog();
                                return false;
                            } else {
                                return true;
                            }
                        }
                    }]
                });
                
                $scope.uploader.onAfterAddingFile = function(item) {
                    var filename = item.file.name;

                    // If a file with the same name already exists, send it's 'rev' value along to avoid conflicts.
                    item._exists = false;
                    angular.forEach(directory.contents, function(file) {
                        if(file.name.toLowerCase() == filename.toLowerCase()) {
                            item._exists = true;
                            item.formData.push({
                                'parent_rev': file.rev
                            });
                        }
                    });
                    
                    // Add file path to POST data
                    item.formData.push({
                        path: directory.path+'/'+filename
                    });
                };
                
                $scope.uploader.onSuccessItem = function(item, response, status, headers) {
                    var data = response;
                    FileRepository.injectFilenames(data);
                    
                    if(item._exists) {
                        $rootScope.$broadcast('fileUpdated', data);
                    } else {
                        $rootScope.$broadcast('fileCreated', data);
                    }
                };
                
                $scope.close = function() {
                    $modalInstance.close();
                };
            },
            resolve: {
                directory: function() { return $scope.directory; }
            }
        });
    };

    $scope.openCreateFolderDialog = function() {
        if(!$scope.directory) return;
        var path = $scope.directory.path;
        
        var modal = $modal.open({
            backdrop: 'static',
            templateUrl: partial('files/create-folder-dialog.html'),
            controller: function($scope, $rootScope, $modalInstance, FileRepository) {
                $scope.nameChanged = function(form) {
                    // Reset invalidName flag when name changes
                    form.name.$setValidity('invalidName', true);
                };

                $scope.create = function(form) {
                    // Create subdirectory
                    FileRepository.createFolder(path+'/'+form.nameValue)
                        .success(function(data) {
                            $rootScope.$broadcast('fileCreated', data);
                            $modalInstance.close();
                        })
                        .error(function(data, status) {
                            if(status == 400) {
                                form.name.$setValidity('invalidName', false);
                            }
                        });
                };
                
                $scope.cancel = function() {
                    $modalInstance.dismiss('cancel');
                };
            }
        });
    };
    
    // Default to browsing team's root directory
    if(NavFilterService.team) {
        $scope.setDirectory('/'+NavFilterService.team.color);
    }
});

module.factory('FileDialogService', function($modal) {
    return {
        openFile: function(file) {
            var modal = $modal.open({
                backdrop: 'static',
                windowClass: 'lg-dialog',
                templateUrl: partial('files/file-dialog.html'),
                controller: function($scope, $modalInstance, FileRepository) {
                    $scope.file = file;
                    
                    var getFileExtension = function(filename) {
                        var i = filename.lastIndexOf('.');
                        return i >= 0 ? filename.substr(i+1) : null;
                    };

                    // Determine whether a file preview is available
                    var previewExts = [
                        'doc', 'docx', 'docm', 'ppt', 'pps',
                        'ppsx', 'ppsm', 'pptx', 'pptm', 'xls',
                        'xlsx', 'xlsm', 'rtf', 'pdf'
                    ];
                    if(previewExts.indexOf(getFileExtension(file.path)) >= 0) {
                        $scope.previewUrl = FileRepository.getPreviewUrl(file.path);
                    }
                    
                    $scope.close = function() {
                        $modalInstance.close();
                    };
                }
            });
            return modal;
        },
        deleteFiles: function(files) {
            var modal = $modal.open({
                backdrop: 'static',
                templateUrl: partial('files/delete-dialog.html'),
                controller: function($scope, $rootScope, $modalInstance, FileRepository) {
                    $scope.files = files;
                    
                    $scope.delete = function() {
                        // Build array of file paths
                        var paths = files.map(function(file) {
                            return file.path;
                        });

                        // Delete files
                        FileRepository.delete(paths)
                            .success(function() {
                                // Broadcast delete messages
                                angular.forEach(files, function(file) {
                                    $rootScope.$broadcast('fileDeleted', file);
                                });
                                
                                $modalInstance.close();
                            });
                    };
                    
                    $scope.cancel = function() {
                        $modalInstance.dismiss('cancel');
                    };
                }
            });
            return modal;
        }
    };
});