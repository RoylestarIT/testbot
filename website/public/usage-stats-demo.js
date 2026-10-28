/**
 * Демо-заглушка статистики для вёрстки. Позже getStats() → реальный API бота.
 */
(function () {
  var CONFIG = {
    storageKey: "gb_usage_stats_demo_v1",
    initialToday: 127,
    initialMonth: 3841,
    tickMinMs: 15000,
    tickMaxMs: 60000,
    bumpMin: 1,
    bumpMax: 5,
    todayResetMin: 90,
    todayResetMax: 160,
  };

  function dayKey(d) {
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function formatRu(n) {
    return new Intl.NumberFormat("ru-RU").format(n);
  }

  function loadState() {
    try {
      var raw = localStorage.getItem(CONFIG.storageKey);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (typeof parsed.today !== "number" || typeof parsed.month !== "number") return null;
      return parsed;
    } catch (_e) {
      return null;
    }
  }

  function saveState(state) {
    try {
      localStorage.setItem(CONFIG.storageKey, JSON.stringify(state));
    } catch (_e) {
      /* private mode */
    }
  }

  function defaultState() {
    return {
      day: dayKey(new Date()),
      today: CONFIG.initialToday,
      month: CONFIG.initialMonth,
    };
  }

  function ensureDay(state) {
    var today = dayKey(new Date());
    if (state.day !== today) {
      state.day = today;
      state.today = randInt(CONFIG.todayResetMin, CONFIG.todayResetMax);
    }
  }

  function render(state) {
    var elToday = document.getElementById("stat-today");
    var elMonth = document.getElementById("stat-month");
    if (elToday) elToday.textContent = formatRu(state.today);
    if (elMonth) elMonth.textContent = formatRu(state.month);
  }

  function bump(state) {
    var inc = randInt(CONFIG.bumpMin, CONFIG.bumpMax);
    state.today += inc;
    state.month += inc;
  }

  function scheduleTick(state) {
    var delay = randInt(CONFIG.tickMinMs, CONFIG.tickMaxMs);
    window.setTimeout(function () {
      bump(state);
      saveState(state);
      render(state);
      scheduleTick(state);
    }, delay);
  }

  function getStats() {
    var state = loadState() || defaultState();
    ensureDay(state);
    saveState(state);
    return Promise.resolve({ today: state.today, month: state.month });
  }

  function init() {
    if (!document.getElementById("stat-today")) return;
    var state = loadState() || defaultState();
    ensureDay(state);
    saveState(state);
    render(state);
    scheduleTick(state);
  }

  window.getStats = getStats;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
