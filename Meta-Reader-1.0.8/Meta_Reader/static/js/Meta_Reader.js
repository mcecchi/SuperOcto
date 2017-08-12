/*
 * View model for Meta_Reader
 *
 * Author: Robo3D
 * License: AGPLv3
 */
$(function() {
    function Meta_readerViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        Meta_readerViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ /* "loginStateViewModel", "settingsViewModel" */ ],

        // e.g. #settings_plugin_Meta_Reader, #tab_plugin_Meta_Reader, ...
        [ /* ... */ ]
    ]);
});
