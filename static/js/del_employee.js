window.onload = () => {
    const $button = document.querySelector('.icon-nav')
    const $list = document.getElementById('nav_list')

    $button.addEventListener('click', () => {
        $list.classList.toggle('translate')
    })
}
