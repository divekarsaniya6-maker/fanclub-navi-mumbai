document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".nav-links");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "✕" : "☰";
    });
    nav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.textContent = "☰";
    }));
  }

  const dateInput = document.getElementById("bookingDate");
  if (dateInput) {
    const today = new Date();
    const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    dateInput.min = localDate;
  }

  document.querySelectorAll("[data-sport]").forEach(link => {
    link.addEventListener("click", () => {
      const select = document.getElementById("sportSelect");
      if (select) select.value = link.dataset.sport;
    });
  });

  document.querySelectorAll(".flash").forEach(msg => {
    window.setTimeout(() => msg.classList.add("flash-fade"), 6000);
  });
});
