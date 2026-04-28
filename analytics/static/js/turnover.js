document.addEventListener("DOMContentLoaded", () => {
    const data = HR.loadEmbeddedData();
    if (!data) return;

    renderTurnover(data.turnover_by_month);
    renderReasons(data.turnover_reasons);
    renderDept(data.turnover_by_department);
    renderGrade(data.turnover_by_grade);
});

function renderTurnover(d) {
    const c = document.getElementById("chartTurnover");
    new Chart(c, {
        type: "line",
        data: {
            labels: d.labels,
            datasets: [
                {
                    label: "Найм", data: d.hired,
                    borderColor: HR.palette.teal, backgroundColor: HR.gradient(c, HR.palette.teal),
                    tension: 0.4, fill: true, pointRadius: 3, pointBackgroundColor: HR.palette.teal, borderWidth: 2.5,
                },
                {
                    label: "Увольнения", data: d.terminated,
                    borderColor: HR.palette.coral, backgroundColor: HR.gradient(c, HR.palette.coral),
                    tension: 0.4, fill: true, pointRadius: 3, pointBackgroundColor: HR.palette.coral, borderWidth: 2.5,
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false, scales: HR.baseScales, plugins: { legend: { position: "top", align: "end" } } },
    });
}

function renderReasons(d) {
    const c = document.getElementById("chartReasons");
    new Chart(c, {
        type: "doughnut",
        data: {
            labels: d.labels,
            datasets: [{ data: d.data, backgroundColor: HR.colorList, borderColor: HR.CARD_BG, borderWidth: 3, hoverOffset: 8 }],
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: "65%", plugins: { legend: { position: "bottom" } } },
    });
}

function renderDept(d) {
    const c = document.getElementById("chartDept");
    new Chart(c, {
        type: "bar",
        data: {
            labels: d.labels,
            datasets: [
                { label: "Активные",  data: d.active,     backgroundColor: HR.palette.emerald, borderRadius: 6, stack: "s" },
                { label: "Уволенные", data: d.terminated, backgroundColor: HR.palette.rose,    borderRadius: 6, stack: "s" },
            ],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                x: { ...HR.baseScales.x, stacked: true },
                y: { ...HR.baseScales.y, stacked: true },
            },
            plugins: { legend: { position: "top", align: "end" } },
        },
    });
}

function renderGrade(d) {
    const c = document.getElementById("chartGrade");
    new Chart(c, {
        type: "bar",
        data: {
            labels: d.labels,
            datasets: [
                { label: "Активные",  data: d.active,     backgroundColor: HR.palette.teal,   borderRadius: 6 },
                { label: "Уволенные", data: d.terminated, backgroundColor: HR.palette.coral,  borderRadius: 6 },
            ],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: HR.baseScales,
            plugins: { legend: { position: "top", align: "end" } },
        },
    });
}
