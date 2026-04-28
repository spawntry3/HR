window.HR = window.HR || {};

HR.palette = {
    teal:    "#0d9488",
    coral:   "#f97316",
    violet:  "#7c3aed",
    pink:    "#ec4899",
    amber:   "#f59e0b",
    cyan:    "#06b6d4",
    rose:    "#f43f5e",
    emerald: "#10b981",
    blue:    "#3b82f6",
    purple:  "#a855f7",
    yellow:  "#facc15",
    lime:    "#84cc16",
};
HR.colorList = Object.values(HR.palette);
HR.TEXT_COLOR = "#475569";
HR.GRID_COLOR = "rgba(15, 23, 42, 0.06)";
HR.CARD_BG = "#ffffff";

Chart.defaults.color = HR.TEXT_COLOR;
Chart.defaults.borderColor = HR.GRID_COLOR;
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.boxWidth = 10;
Chart.defaults.plugins.legend.labels.boxHeight = 10;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.tooltip.backgroundColor = "#0f172a";
Chart.defaults.plugins.tooltip.titleColor = "#f8fafc";
Chart.defaults.plugins.tooltip.bodyColor = "#e2e8f0";
Chart.defaults.plugins.tooltip.borderColor = "rgba(255,255,255,0.08)";
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;

HR.fmtMoney = v => new Intl.NumberFormat("kk-KZ").format(Math.round(v)) + " ₸";

HR.baseScales = {
    x: { grid: { display: false }, ticks: { color: HR.TEXT_COLOR } },
    y: { grid: { color: HR.GRID_COLOR }, ticks: { color: HR.TEXT_COLOR } },
};

HR.gradient = function (canvas, color) {
    const c = canvas.getContext("2d");
    const h = canvas.clientHeight || canvas.height || 300;
    const g = c.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, color + "55");
    g.addColorStop(1, color + "05");
    return g;
};

HR.loadEmbeddedData = function (id = "chart-data") {
    const node = document.getElementById(id);
    if (!node) {
        console.error("Не найден встроенный JSON блок", id);
        return null;
    }
    try {
        return JSON.parse(node.textContent);
    } catch (e) {
        console.error("Не удалось распарсить встроенные данные", e);
        return null;
    }
};
