let slideIndex = 0;
showSlides();

function showSlides() {
    let slides = document.getElementsByClassName("slide");
    
    for (let i = 0; i < slides.length; i++) {
        slides[i].style.opacity = "0";
    }
    
    slideIndex++;
    if (slideIndex > slides.length) {slideIndex = 1}
    
    slides[slideIndex-1].style.opacity = "1";
    setTimeout(showSlides, 5000); // Change image every 5 seconds
}


// Enhanced Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    const body = document.body;

    navToggle.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        navToggle.classList.toggle('active');
        body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
            navLinks.classList.remove('active');
            navToggle.classList.remove('active');
            body.style.overflow = '';
        }
    });

    // Close menu when clicking a link
    const links = navLinks.getElementsByTagName('a');
    Array.from(links).forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            navToggle.classList.remove('active');
            body.style.overflow = '';
        });
    });
});
