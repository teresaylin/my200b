var module = angular.module('events', []);

module.controller('EventDetailStateCtrl', function($scope, $stateParams, EventRepository) {
    // Get event
    EventRepository.get($stateParams.eventId)
        .success(function(event) {
            $scope.event = event;
        });
        
    $scope.addAttendee = function(user) {
        EventRepository.addAttendee($scope.event.id, user.id)
            .success(function() {
                $scope.event.attendees.push(user);
            });
    };

    $scope.removeAttendee = function(user) {
        EventRepository.removeAttendee($scope.event.id, user.id)
            .success(function() {
                var attendees = $scope.event.attendees;
                attendees.splice(attendees.indexOf(user), 1);
            });
    };
});

module.controller('EventDialogCtrl', function($scope, $modalInstance, EventRepository, EventDialogService, FileRepository, FileDialogService, event) {
    var changesMade = false; // This is set when an event is created/edited
    
    var loadEvent = function(eventData) {
        $scope.event = eventData;
        $scope.creating = false;
        $scope.editing = false;
        
        $scope.event.start = new Date($scope.event.start).toISOString();
        $scope.event.end = new Date($scope.event.end).toISOString();
    };
    
    var newEvent = function() {
        var now = moment();
        $scope.event = {
            // Initialize start and end times
            start: now.clone().toISOString(),
            end: now.clone().add(1, 'hours').toISOString()
        };
        $scope.creating = true;
        $scope.editing = true;
    };
    
    if(event) {
        // Opening existing event
        loadEvent(angular.copy(event));
    } else {
        // Creating new event
        newEvent();
    }
    
    $scope.edit = function() {
        $scope.editing = true;
    };
    
    $scope.create = function(form) {
        // Create event
        EventRepository.create($scope.event)
            .success(function(data) {
                changesMade = true;
                // Refresh event with returned data
                loadEvent(data);
                form.$setPristine();
            });
    };

    $scope.update = function(form) {
        // Update event
        EventRepository.update($scope.event.id, $scope.event)
            .success(function(data) {
                changesMade = true;
                // Refresh event with returned data
                loadEvent(data);
                form.$setPristine();
            });
    };
    
    $scope.delete = function() {
        // Open delete event dialog
        EventDialogService.deleteEvent(event).result
            .then(function(deleted) {
                if(deleted) {
                    $modalInstance.close(true);
                }
            });
    };

    $scope.close = function() {
        $modalInstance.close(changesMade);
    };
        
    $scope.addAttendee = function(user) {
        EventRepository.addAttendee($scope.event.id, user.id)
            .success(function() {
                $scope.event.attendees.push(user);
                changesMade = true;
            });
    };

    $scope.addAttendeeTaskforce = function(taskforce) {
        EventRepository.addAttendeeTaskforce($scope.event.id, taskforce.id)
            .success(function(data) {
                $scope.event.attendees = data.attendees;
                changesMade = true;
            });
    };

    $scope.removeAttendee = function(user) {
        EventRepository.removeAttendee($scope.event.id, user.id)
            .success(function() {
                var attendees = $scope.event.attendees;
                attendees.splice(attendees.indexOf(user), 1);
                changesMade = true;
            });
    };

    $scope.addFile = function(path) {
        EventRepository.addFile($scope.event.id, path)
            .success(function() {
                $scope.event.files.push(path);
                changesMade = true;
            });
    };

    $scope.removeFile = function(path) {
        EventRepository.removeFile($scope.event.id, path)
            .success(function() {
                var files = $scope.event.files;
                files.splice(files.indexOf(path), 1);
                changesMade = true;
            });
    };
    
    $scope.openFile = function(path) {
        FileRepository.metadata(path)
            .success(function(file) {
                FileDialogService.openFile(file);
            });
    };
});

module.factory('EventDialogService', function($modal) {
    return {
        openEvent: function(event) {
            var modal = $modal.open({
                backdrop: 'static',
                templateUrl: partial('events/event-dialog.html'),
                controller: 'EventDialogCtrl',
                resolve: {
                    event: function() {
                        return event;
                    }
                }
            });
            
            return modal;
        },
        newEvent: function() {
            return this.openEvent(null);
        },
        deleteEvent: function(event) {
            var modal = $modal.open({
                backdrop: 'static',
                templateUrl: partial('events/delete-dialog.html'),
                controller: function($scope, $modalInstance, EventRepository, event) {
                    $scope.event = event;
                    
                    $scope.delete = function() {
                        // Delete event
                        EventRepository.delete($scope.event.id)
                            .success(function() {
                                $modalInstance.close(true);
                            });
                    };
                    
                    $scope.cancel = function() {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                    event: function() {
                        return event;
                    }
                }
            });
            
            return modal;
        }
    };
});

module.controller('CalendarCtrl', function($scope, $modal, $state, EventRepository, EventDialogService, NavFilterService) {
    $scope.eventsSource = function(start, end, timezone, callback) {
        // Get events within date range
        if(NavFilterService.team) {
            var query = {
                start: start.toJSON(),
                end: end.toJSON(),
                team: NavFilterService.team.id
            };

            EventRepository.list(query)
                .success(function(events) {
                    callback(events);
                });
        };
    };
    
    $scope.$on('navFilterChanged', function(event, changed) {
        if('team' in changed && 'calendar' in $scope) {
            // Reload events
            $scope.calendar.fullCalendar('refetchEvents');
        }
    });

    // Event click handler
    var onEventClick = function(event, allDay, jsEvent, view){
        var dlg = EventDialogService.openEvent(event);

        dlg.result.then(function(changesMade) {
            if(changesMade) {
                // Reload events
                $scope.calendar.fullCalendar('refetchEvents');
            }
        });
    };

    // Event drag/drop handler
    var onEventDrop = function(event, delta, revertFunc, jsEvent, ui, view) {
    };

    // Event resize handler
    var onEventResize = function(event, delta, revertFunc, jsEvent, ui, view) {
    };

    // Calendar configuration
    $scope.uiConfig = {
        calendar: {
            aspectRatio: 2,
            header: {
                left: 'agendaDay agendaWeek month',
                center: 'title',
                right: 'today prev,next'
            },
            allDaySlot: false,
            timezone: 'local',
            eventClick: onEventClick,
            eventDrop: onEventDrop,
            eventResize: onEventResize
        }
    };

    $scope.eventSources = [$scope.eventsSource];
    
    $scope.newEvent = function() {
        var dlg = EventDialogService.newEvent();

        dlg.result.then(function(changesMade) {
            if(changesMade) {
                // Reload events
                $scope.calendar.fullCalendar('refetchEvents');
            }
        });
    };
});

module.directive('calendar', function() {
    return {
        restrict: 'E',
        scope: {},
        templateUrl: 'events/calendar.html',
        controller: 'CalendarCtrl'
    };
});