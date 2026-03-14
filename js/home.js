(function () {
  var header = document.querySelector(".site-header");
  var navToggle = document.querySelector(".nav-toggle");
  var navMenu = document.querySelector(".nav-menu");
  var typedRole = document.getElementById("typed-role");
  var revealItems = document.querySelectorAll(".reveal");
  var roles = [
    "Android Framework Internals",
    "Jetpack Architecture Components",
    "Performance Optimization Notes",
    "Source Code Reading Workflow"
  ];
  var roleIndex = 0;

  function syncHeaderState() {
    if (!header) {
      return;
    }

    if (window.scrollY > 24) {
      header.classList.add("is-scrolled");
    } else {
      header.classList.remove("is-scrolled");
    }
  }

  function rotateRole() {
    if (!typedRole) {
      return;
    }

    typedRole.textContent = roles[roleIndex];
    roleIndex = (roleIndex + 1) % roles.length;
  }

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", function () {
      var isOpen = navMenu.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });

    navMenu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        navMenu.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.16
    });

    revealItems.forEach(function (item) {
      observer.observe(item);
    });
  } else {
    revealItems.forEach(function (item) {
      item.classList.add("is-visible");
    });
  }

  rotateRole();
  window.setInterval(rotateRole, 2400);
  syncHeaderState();
  window.addEventListener("scroll", syncHeaderState, { passive: true });
})();
