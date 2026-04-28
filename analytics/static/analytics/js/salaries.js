document.addEventListener("DOMContentLoaded", () => {
    const data = HR.loadEmbeddedData();
    if (!data) return;

    renderGradeSalary(data.salary_by_grade);
    renderHeadcount(data.headcount_by_department);
    renderStackSalary(data.salary_by_stack);
    renderSalaryDist(data.salary_distribution);
    renderDeptSalary(data.salary_by_department);
});

function renderGradeSalary(d) {
    const c = document.getElementById("chartGradeSalary");
    new Chart(c, {
        type: "bar",
        data: {
            labels: d.labels,
            datasets: [
                { label: "Мин",     data: d.min, backgroundColor: HR.palette.cyan,   borderRadius: 6 },
                { label: "Средняя", data: d.avg, backgroundColor: HR.palette.violet, borderRadius: 6 },
                { label: "Макс",    data: d.max, backgroundColor: HR.palette.coral,  borderRadius: 6 },
            ],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                x: HR.baseScales.x,
                y: { ...HR.baseScales.y, ticks: { ...HR.baseScales.y.ticks, callback: v => Math.round(v / 1000) + "k" } },
            },
            plugins: {
                legend: { position: "top", align: "end" },
                tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${HR.fmtMoney(ctx.parsed.y)}` } },
            },
        },
    });
}

function renderHeadcount(d) {
    const c = document.getElementById("chartHeadcount");
    new Chart(c, {
        type: "polarArea",
        data: {
            labels: d.labels,
            datasets: [{
                data: d.data,
                backgroundColor: d.labels.map((_, i) => HR.colorList[i % HR.colorList.length] + "cc"),
                borderColor: HR.CARD_BG, borderWidth: 2,
            }],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: "right" } },
            scales: { r: { ticks: { display: false }, grid: { color: HR.GRID_COLOR } } },
        },
    });
}

function renderStackSalary(d) {
    const c = document.getElementById("chartStackSalary");
    new Chart(c, {
        type: "bar",
        data: {
            labels: d.labels,
            datasets: [{
                label: "Средняя ЗП", data: d.avg,
                backgroundColor: d.labels.map((_, i) => HR.colorList[i % HR.colorList.length]),
                borderRadius: 6,
            }],
        },
        options: {
            indexAxis: "y", responsive: true, maintainAspectRatio: false,
            scales: {
                y: { ...HR.baseScales.y, grid: { display: false } },
                x: { ...HR.baseScales.y, ticks: { ...HR.baseScales.y.ticks, callback: v => Math.round(v / 1000) + "k" } },
            },
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => `${HR.fmtMoney(ctx.parsed.x)} (${d.count[ctx.dataIndex]} чел.)` } },
            },
        },
    });
}

function renderSalaryDist(d) {
    const c = document.getElementById("chartSalaryDist");
    new Chart(c, {
        type: "bar",
        data: {
            labels: d.labels,
            datasets: [{
                label: "Сотрудники", data: d.data,
                backgroundColor: HR.gradient(c, HR.palette.violet),
                borderColor: HR.palette.violet, borderWidth: 2, borderRadius: 4,
            }],
        },
        options: { responsive: true, maintainAspectRatio: false, scales: HR.baseScales, plugins: { legend: { display: false } } },
    });
}

function renderDeptSalary(d) {
    const c = document.getElementById("chartDeptSalary");
    new Chart(c, {
        type: "bar",
        data: {
            labels: d.labels,
            datasets: [{
                label: "Средняя ЗП", data: d.avg,
                backgroundColor: HR.palette.teal, borderRadius: 6,
            }],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                x: HR.baseScales.x,
                y: { ...HR.baseScales.y, ticks: { ...HR.baseScales.y.ticks, callback: v => Math.round(v / 1000) + "k" } },
            },
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => `${HR.fmtMoney(ctx.parsed.y)} (${d.count[ctx.dataIndex]} чел.)` } },
            },
        },
    });
}
