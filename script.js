// Subtle reveal for the feature cards only — everything else on the page
// is static, so this is the one deliberate motion moment.
const cards = document.querySelectorAll('.feature-card');

if ('IntersectionObserver' in window && cards.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  cards.forEach((card) => observer.observe(card));
} else {
  cards.forEach((card) => card.classList.add('visible'));
}
