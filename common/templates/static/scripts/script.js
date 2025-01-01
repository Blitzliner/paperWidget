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
    toast('Preview ' + app_name);
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
        toast('Show image preview');
    } else {
        toast('No Image selected');
    }
    _update_address('');
}

function toast(message) {
    const el = document.getElementById('toast');
    el.innerHTML = message;
    el.className = 'show';
    setTimeout(function() {
        el.className = el.className.replace("show", "");
    }, 3000);
}

function submit(button, form, endpoint) {
    button.addEventListener('click', async function(event) {
        event.preventDefault(); // Prevent the default form submission
        var formData = (form) ? new FormData(form) : {};
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { Accept: 'application/json' },
                body: formData
            });
            const result = await response.json();

            if (response.ok) {
                toast(`Success: ${result.message}`);
            } else {
                toast(`Error: ${result.detail}`);
            }
        } catch (error) {
            toast(`Error: ${error.message}`);
        }
    });
}

function upload(button, form, endpoint) {
    button.addEventListener('click', async function(event) {
        event.preventDefault();
        var file = document.getElementById("file_upload").files[0];
        if (file) {
            const formData = new FormData(form);
            try {
                const response = await fetch(endpoint, {
                  method: "POST",
                  body: formData,
                });
                const result = await response.json();

                if (response.ok) {
                    toast(`Success: ${result.message}`);
                } else {
                    toast(`Error: ${result.detail}`);
                }
            } catch (error) {
                toast(`Error: ${error.message}`);
            }
        } else {
            toast('No Image selected.')
        }
    });
}

// wait for document is ready
document.addEventListener('DOMContentLoaded', function(event) {
    // app preview
    document.querySelectorAll("form.app .btn_preview").forEach(el => {
        el.addEventListener('click', function(event) {
            var currElement = event.target;
            loadAddressInIframe(currElement);
        });
    });
    // app settings update
    document.querySelectorAll("form.app .btn_save").forEach(el => {
        const form = el.parentNode;  //closest('form');
        const app_id = form.querySelector('input[name="app_id"]').value;
        submit(el, form, '/apps/' + app_id);
    });
    document.querySelector("form.image_upload .btn_preview").addEventListener("click", function(event) {
        loadImageInIframe(event.target);
    });
    upload(document.querySelector("form.image_upload .btn_upload"), document.querySelector("form.image_upload"), "/upload")
    submit(document.querySelector("form.general .btn_save"), document.querySelector("form.general"), "/general/save");
    submit(document.querySelector("form.general .btn_update"), null, "/general/update");
});
