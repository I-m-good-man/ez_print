$(document).ready(function () {
    let color_print_checkbox = document.querySelector('#color_print_checkbox')
    let monochrome_print_checkbox = document.querySelector('#monochrome_print_checkbox')
    let flip_over_mode_checkbox = document.querySelector('#flip_over_mode_checkbox')
    let num_of_copies_field = document.querySelector('#num_of_copies_field')

    let color_print_available = true;
    if (color_print_checkbox.style.pointerEvents === 'none') {
        color_print_available = false;
    }

    let monochrome_print_available = true;
    if (monochrome_print_checkbox.style.pointerEvents === 'none') {
        monochrome_print_available = false;
    }
    color_print_checkbox.addEventListener('click', (event) => {
        if (color_print_checkbox.checked === false) {
            if (monochrome_print_available === false) {
                color_print_checkbox.checked = true;
            } else {
                monochrome_print_checkbox.checked = true;
            }
        } else {
            monochrome_print_checkbox.checked = false;
        }

    });

    monochrome_print_checkbox.addEventListener('click', (event) => {
        if (monochrome_print_checkbox.checked === false) {
            if (color_print_available === false) {
                monochrome_print_checkbox.checked = true;
            } else {
                color_print_checkbox.checked = true;
            }
        } else {
            color_print_checkbox.checked = false;
        }
    });

    $('#printer_settings_form').submit(function (event) {
        $('.text_loading').html('Считаем...');
        document.getElementById('loader_container').style.display = 'flex';
        document.body.style.overflow = 'hidden';

        let xhr = new XMLHttpRequest();
        var url_for_ajax_request = document.querySelector('#printer_settings_form').getAttribute('action')
        xhr.open("POST", url_for_ajax_request, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        var data = JSON.stringify({
            "monochrome_printing_mode": monochrome_print_checkbox.checked,
            "color_printing_mode": color_print_checkbox.checked,
            "flip_over_mode": flip_over_mode_checkbox.checked,
            "num_of_copies": parseInt(num_of_copies_field.value)
        });
        xhr.send(data)
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                document.getElementById('loader_container').style.display = 'none';
                document.body.style.overflow = 'visible';

                var jsonResponse = JSON.parse(xhr.responseText);
                if (jsonResponse.status === 'ok') {
                    reponse_section = document.getElementById('html_response');
                    reponse_section.innerHTML = jsonResponse.html_element;
                } else if (jsonResponse.status === 'redirect') {
                    document.location.href = jsonResponse.link;
                } else if (jsonResponse.status === 'error') {
                    reponse_section = document.getElementById('html_response');
                    reponse_section.innerHTML = jsonResponse.html_element;
                }

            }
        };

        return false;
    });

});