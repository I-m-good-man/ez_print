$(document).ready(function () {
    $('#task_is_paid').click(function () {
        document.getElementById('task_is_paid').style.display = 'none';

        $('.text_loading').html('Печатаем...');
        document.getElementById('loader_container').style.display = 'flex';
        document.body.style.overflow = 'hidden';

        var link_to_print_task = document.getElementById('print_task_form').getAttribute('action')
        var link_to_get_info_about_printing_task = document.getElementById('get_info_about_printing_task_form').getAttribute('action')
        httpGet(link_to_print_task)
            .then(
                jsonResponse => {
                    if (jsonResponse.status === 'ok') {
                        var counter = 10;
                        var start_time = Date.now();
                        var delay_between_requests_ms = 5000;
                        // var time_for_all_requests_ms = counter * delay_between_requests_ms;
                        var time_for_all_requests_ms = 100 * 6000;
                        get_info(link_to_get_info_about_printing_task, counter, start_time, delay_between_requests_ms, time_for_all_requests_ms);
                    } else if (jsonResponse.status === 'error') {
                        document.getElementById('error_task_status').style.display = 'block';

                        document.getElementById('loader_container').style.display = 'none';
                        document.body.style.overflow = 'visible';
                    } else if (jsonResponse.status === 'redirect') {
                        document.getElementById('loader_container').style.display = 'none';
                        document.body.style.overflow = 'visible';
                        document.location.href = jsonResponse.link;
                    }
                },
                error => {
                }
            );
        return false;
    });

});

function get_info(link_to_get_info_about_printing_task, counter, start_time, delay_between_requests_ms, time_for_all_requests_ms) {
    return httpGet(link_to_get_info_about_printing_task)
        .then(
            jsonResponse => {
                if (jsonResponse.status === 'successfully_printed') {
                    document.getElementById('success_task_status').style.display = 'block';

                    document.getElementById('loader_container').style.display = 'none';
                    document.body.style.overflow = 'visible';
                    counter = -1;
                } else if (jsonResponse.status === 'occurred_error_while_printing') {
                    document.getElementById('error_task_status').style.display = 'block';

                    document.getElementById('loader_container').style.display = 'none';
                    document.body.style.overflow = 'visible';
                    counter = -1;
                } else if (jsonResponse.status === 'printing_in_process') {
                } else if (jsonResponse.status === 'redirect') {
                    document.getElementById('loader_container').style.display = 'none';
                    document.body.style.overflow = 'visible';
                    counter = -1;

                    document.location.href = jsonResponse.link;
                }
            },
            error => {
            }
        )
        .finally(() => waitFor(delay_between_requests_ms)) // задержка между вызовами рекурсии
        .then(() => {
            // проверка того, сколько всего времени прошло с момента первого запроса, чтобы прервать
            // время,
            if (Date.now() - start_time < time_for_all_requests_ms) {
                // проверка счетчика запроса, если больше запросов нет, то задача не выполнена
                // иначе еще раз вызывается функция, чтобы сделать запрос
                if (counter > 0) {
                    get_info(link_to_get_info_about_printing_task, counter - 1, start_time, delay_between_requests_ms, time_for_all_requests_ms)
                } else if (counter === -1) {
                    // если череда ajax запросов привела к какому то выводу на сайт - успех или
                    // провал, то counter=-1, чтобы перестать слать запросы на сервер
                } else {
                    document.getElementById('error_task_status').style.display = 'block';

                    document.getElementById('loader_container').style.display = 'none';
                    document.body.style.overflow = 'visible';
                    counter = -1;
                }
            } else {
                document.getElementById('error_task_status').style.display = 'block';

                document.getElementById('loader_container').style.display = 'none';
                document.body.style.overflow = 'visible';
                counter = -1;
            }
        })
}

function waitFor(ms) {
    return new Promise((resolve) => {
        setTimeout(resolve, ms);
    })
}

function httpGet(url) {

    return new Promise(function (resolve, reject) {

        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);

        xhr.onload = function () {
            if (this.status == 200) {
                var jsonResponse = JSON.parse(xhr.responseText);
                resolve(jsonResponse);
            } else {
                reject('error');
            }
        };

        xhr.onerror = function () {
            reject(new Error("Network Error"));
        };

        xhr.send();
    });

}