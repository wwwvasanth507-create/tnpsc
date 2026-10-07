// Global Vanilla JS Logic
document.addEventListener('DOMContentLoaded', () => {
    // Mobile Drawer Toggle
    const mobileBtn = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
});
