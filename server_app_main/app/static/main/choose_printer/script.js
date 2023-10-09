let count_of_batch_of_cards = 1;

function checkPosition() {
    const height = document.body.offsetHeight - document.getElementById('footer').offsetHeight
    const screenHeight = window.innerHeight
    const scrolled = window.scrollY
    const threshold = height - screenHeight / 4
    const position = scrolled + screenHeight
    if (position >= threshold) {
        if (count_of_batch_of_cards != -1) {
            count_of_batch_of_cards = count_of_batch_of_cards + 1;
            url_for_ajax_request = document.getElementById('link_for_new_batch_of_printers').getAttribute("href");
            let xhr = new XMLHttpRequest();
            xhr.open("POST", url_for_ajax_request, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            var data = JSON.stringify({"num_of_batch": count_of_batch_of_cards});
            xhr.send(data)
            xhr.onreadystatechange = function () {

                if (xhr.readyState === 4 && xhr.status === 200) {
                    var jsonResponse = JSON.parse(xhr.responseText);
                    if (jsonResponse.status == 'ok') {
                        row = document.getElementById('card_row');
                        row.innerHTML = row.innerHTML + jsonResponse.html_element;
                    } else {
                        count_of_batch_of_cards = -1;
                        m = document.getElementById('main-content');
                        // m.innerHTML = m.innerHTML + '<header>Больше принтеров нет!</header>';
                    }
                }
            };

        }
    }
}

function throttle(callee, timeout) {
    let timer = null

    return function perform(...args) {
        if (timer) return

        timer = setTimeout(() => {
            callee(...args)

            clearTimeout(timer)
            timer = null
        }, timeout)
    }
}

window.addEventListener('scroll', throttle(checkPosition, 250))
window.addEventListener('resize', throttle(checkPosition, 250))

