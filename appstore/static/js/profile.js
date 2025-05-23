document.querySelectorAll('.collapsible').forEach(button => {
    button.addEventListener('click', () => {
        button.classList.toggle('active');
        const content = button.nextElementSibling;

        if (content.style.maxHeight) {
            content.style.maxHeight = null;
            content.classList.remove('expanded');
        } else {
            content.style.maxHeight = content.scrollHeight + 30 + 'px';
            content.classList.add('expanded');
        }
    });
});