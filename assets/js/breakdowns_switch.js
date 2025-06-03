document.getElementById('breakdown-switch').addEventListener('change', function() {
    const elements = document.querySelectorAll('[has_breakdown="false"]');
    elements.forEach(element => {
        element.style.display = this.checked ? 'none' : '';
    });

    const ribbons = document.querySelectorAll('.ribbon');
    ribbons.forEach(ribbon => {
        ribbon.style.display = this.checked ? 'none' : '';
    });
});
