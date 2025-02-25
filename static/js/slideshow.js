document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slide');
    let currentSlide = 0;

    // Initialize first slide
    if (slides.length > 0) {
        slides[0].classList.add('active');
    }

    function nextSlide() {
        slides[currentSlide].classList.remove('active');
        currentSlide = (currentSlide + 1) % slides.length;
        slides[currentSlide].classList.add('active');
    }

    function previousSlide() {
        slides[currentSlide].classList.remove('active');
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        slides[currentSlide].classList.add('active');
    }

    const slideshow = document.querySelector('.slideshow');
    let slideshowInterval;

    function startSlideshow() {
        slideshowInterval = setInterval(nextSlide, 5000);
    }

    function pauseSlideshow() {
        clearInterval(slideshowInterval);
    }

    // Pause on hover
    slideshow.addEventListener('mouseenter', pauseSlideshow);
    slideshow.addEventListener('mouseleave', startSlideshow);

    // Click navigation
    slideshow.addEventListener('click', function(e) {
        const rect = slideshow.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        
        // Click on left half goes to previous slide, right half goes to next slide
        if (clickX < rect.width / 2) {
            previousSlide();
        } else {
            nextSlide();
        }
        
        // Reset the interval to prevent immediate automatic transition
        pauseSlideshow();
        startSlideshow();
    });

    // Touch navigation
    let touchStartX = 0;
    let touchEndX = 0;

    slideshow.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].clientX;
        pauseSlideshow();
    });

    slideshow.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].clientX;
        
        // Determine swipe direction
        if (touchStartX - touchEndX > 50) { // Swipe left
            nextSlide();
        } else if (touchEndX - touchStartX > 50) { // Swipe right
            previousSlide();
        }
        
        startSlideshow();
    });

    // Start the slideshow
    startSlideshow();
});
