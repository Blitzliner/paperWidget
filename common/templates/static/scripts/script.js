'use strict'

function loadAddressInIframe(eventElement) {
    // get form to which the preview belongs to
    var form = eventElement.parentNode;
    // get the app name
    var app_name = form.querySelector('input[name="app_name"]').value;
    // the first fieldset are the general settings, and the second input is the address
    var address = form.querySelector('input[name="app_base_address"').value;
    console.log("address: " + address);
    // the second fieldset is the parameter list check if it is available
    var fields = form.querySelectorAll("fieldset");
    if (fields.length > 1) {
        var params = fields[1].querySelectorAll("input");
        var params_arr = []
        // loop over all parameters and add to list
        for (var i = 0; i < params.length; i++){
            var p = params[i];
            params_arr.push(encodeURIComponent(p.name) + "=" + encodeURIComponent(p.value));
        }
        var params_str = params_arr.join("&");
        // add parameters to the address
        if (params_str.length > 0) {
            address += "?" + params_str;
            console.log("address with parameters: " + address);
        }
    }
    // set source property of iframe
    const preview = document.getElementById("iframe_preview");
    preview.setAttribute("src", address);
    showSnackbar('Preview website for ' + app_name);
    _update_address(address);
}

function _update_address(address) {
    const preview = document.getElementById("preview_address");
    preview.value = address;
}

function loadImageInIframe(eventElement) {
    var file = document.getElementById("file_upload").files[0];
    if (file) {
        // Make a file reader to interpret the file
        var reader = new FileReader();
        // When the reader is done reading
        reader.onload = function(event) {
            var preview = document.getElementById("iframe_preview");
            preview.src = event.target.result
        };
        // Tell the reader to start reading asynchrounously
        reader.readAsDataURL(file);
        showSnackbar('Show image preview');
    } else {
        showSnackbar('No Image selected');
    }
    _update_address('');
}

function showSnackbar(message) {
    const snackbar = document.getElementById('snackbar');
    snackbar.innerHTML = message;
    snackbar.className = 'show';
    setTimeout(function() {
        snackbar.className = snackbar.className.replace("show", "");
    }, 3000);
}

// wait for document is ready
document.addEventListener('DOMContentLoaded', function(event) {
    // get all preview buttons
    var elements = document.getElementsByClassName("btn_preview");
    // loop over all preview buttons and attach an event
    for (var i = 0; i < elements.length; i++) {
        elements[i].addEventListener('click', function(event) {
            var currElement = event.target;
            // special case for the file upload. Not nice but it works..
            if (currElement.parentNode.querySelectorAll("input").length == 1) {
                loadImageInIframe(currElement);
            } else {
                loadAddressInIframe(currElement);
            }
        }, true);
    }
    /* snackbar */

})
