$(document).ready(function () {
    const invalid_extension = document.querySelector('#invalid_extension')
    const invalid_size_of_document = document.querySelector('#invalid_size_of_document')
    const invalid_counting_of_pages = document.querySelector('#invalid_counting_of_pages')
    const lack_of_pages_in_printer = document.querySelector('#lack_of_pages_in_printer')


    const list_of_available_extensions = ['docx', 'pdf', 'odt'];
    const max_document_size = 1024 * 1024 * 50; // в байтах

    const form = document.querySelector(".file-form"),
        fileInput = document.querySelector(".file-input")
    sendFileInput = document.querySelector(".send-file")

    form.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.onchange = ({target}) => {
        let file = target.files[0];

        let ext = "не определилось";
        let parts = file.name.split('.');
        if (parts.length > 1) ext = parts.pop();

        let size_of_document = file.size;

        invalid_extension.style.display = 'none';
        invalid_size_of_document.style.display = 'none';
        invalid_counting_of_pages.style.display = 'none';
        lack_of_pages_in_printer.style.display = 'none';

        if (file) {
            if (size_of_document <= max_document_size){
                if (list_of_available_extensions.includes(ext)){
                    sendFileInput.click();
                }
                else{
                    invalid_extension.style.display = 'block';
                }
            }
            else{
                invalid_size_of_document.style.display = 'block';
            }
        }
        else{
            invalid_counting_of_pages.style.display = 'block';
        }
    }

    $('#uploadForm').submit(function (event) {
        if ($('#uploadFile').val()) {
            event.preventDefault();
            $(this).ajaxSubmit({
                uploadProgress: function () {
                    $('.text_loading').html('Загрузка...');
                    document.getElementById('loader_container').style.display = 'flex';
                    document.body.style.overflow = 'hidden';
                },
                success: function (data) {
                    invalid_extension.style.display = 'none';
                    invalid_size_of_document.style.display = 'none';
                    invalid_counting_of_pages.style.display = 'none';
                    lack_of_pages_in_printer.style.display = 'none';
                    $('#success_area').html("");

                    document.getElementById('loader_container').style.display = 'none';
                    document.body.style.overflow = 'visible';

                    if (data.status === "ok") {
                        $('#uploaded_area').html(data.html_element);
                        // $('#success_area').html(data.success_area);

                    } else if (data.status === "error") {
                        if (data.error_msg === 'FileExtensionError'){
                            invalid_extension.style.display = 'block';
                        }
                        else if (data.error_msg === 'FileSizeError'){
                            invalid_size_of_document.style.display = 'block';
                        }
                        else if (data.error_msg === 'FilePagesError'){
                            invalid_counting_of_pages.style.display = 'block';
                        }
                        else if (data.error_msg === 'LackOfPagesInPrinter'){
                            lack_of_pages_in_printer.style.display = 'block';
                        }
                    } else if (data.status === "redirect") {
                        document.location.href = data.link;
                    }
                },
                resetForm: true
            });
        }
        return false;
    });

    $('#next_step_form').submit(function (event) {
        let uploaded_area_container = document.getElementById('uploaded_area_container');
        let consistent_of_container = uploaded_area_container.querySelectorAll('.row')
        if (consistent_of_container.length === 0) {
            $('#error_area').html('<p class="error-msg">Сначала загрузите документы для печати!</p>');
            event.preventDefault();
            return false;

        } else {
            return true;
        }
    });
});

function delete_file(form) {
    $('.text_loading').html('Удаление...');
    document.getElementById('loader_container').style.display = 'flex';
    document.body.style.overflow = 'hidden';

    $(form).ajaxSubmit({
        success: function (data) {
            document.getElementById('loader_container').style.display = 'none';
            document.body.style.overflow = 'visible';
            if (data.status === "ok" || data.status === "error") {
                $('#uploaded_area').html(data.html_element);
                $('#success_area').html("");
            } else if (data.status === "redirect") {
                document.location.href = data.link;
            }
        },
        resetForm: true
    });
    return false;
}