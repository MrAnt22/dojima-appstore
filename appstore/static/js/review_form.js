try {
    document.getElementById('toggle-review-form').addEventListener('click', function() {
        let form;

        try {
            form = document.getElementById('review-form');
        } catch(e) {
            console.info("Not an app post: ", e);
            return e;
        }
        
        form.classList.toggle('hidden');
        this.textContent = form.classList.contains('hidden') ? 'Write your review' : 'Hide review form';
    });
} catch(e) {
    console.info("Not an app post: ", e);
}
