function loadAddressInIframe(eventElement) {
    // get form to which the preview belongs to
    var form = eventElement.parentNode;
    // get the two fieldsets
    var fields = form.querySelectorAll("fieldset");
    // the first fieldset are the general settings, and the second input is the address
    var address = fields[0].querySelectorAll('input[name="app_base_address"')[0].value;
    console.log("address: " + address);
    // the second fieldset is the parameter list
    var params = fields[1].querySelectorAll("input");
    var params_arr = []
    // loop over all parameters and add to list
    for (i=0; i<params.length; i++){
        var p = params[i];
        params_arr.push(encodeURIComponent(p.name) + "=" + encodeURIComponent(p.value));
    }
    var params_str = params_arr.join("&");
    // add parameters to the address
    if (params_str.length > 0) {
        address += "?" + params_str;
        console.log("address with parameters: " + address);
    }
    // set source property of iframe
    var preview = document.getElementById("iframe_preview");
    preview.setAttribute("src", address);
    _update_address(address);
}

function _update_address(address) {
    preview = document.getElementById("preview_address");
    preview.value = address;
}

function loadImageInIframe(eventElement) {
    var file = document.getElementById("file_upload").files[0];
    console.log(file);
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
    } else {
        console.log("no file selected");
    }
    _update_address('');
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
})