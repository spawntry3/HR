document.addEventListener("DOMContentLoaded", () => {
    const data = HR.loadEmbeddedData();
    if (!data) return;

    renderTurnover(data.turnover_by_month);
    renderReasons(data.turnover_reasons);
    renderGradeSalary(data.salary_by_grade);
    renderStackSalary(data.salary_by_stack);
    renderSalaryDist(data.salary_distribution);
    renderTtcDept(data.time_to_close_by_department);
    renderTtcGrade(data.time_to_close_by_grade);
    renderHeadcount(data.headcount_by_department);
    renderStackPop(data.stack_popularity);
    renderVacStatus(data.vacancies_status);
});

function renderTurnover(d) {
    const c = document.getElementById("chartTurnover");
    new Chart(c, {
        type: "line",
        data: {
            labels: d.labels,
            datasets: [
                {
                    label: "Найм",
                    data: d.hired,
                    borderColor: HR.palette.teal,
                    backgroundColor: HR.gradient(c, HR.palette.teal),
                    tension: 0.4,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: HR.palette.teal,
                    borderWidth: 2.5,
                },
                {
                    label: "Увольнения",
                    data: d.terminated,
                    borderColor: HR.palette.coral,
                    backgroundColor: HR.gradient(c, HR.palette.coral),
                    tension: 0.4,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: HR.palette.coral,
                    borderWidth: 2.5,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: HR.baseScales,
            plugins: { legend: { position: "top", align: "end" } },
        },
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
        options: {
            responsive: true, maintainAspectRatio: false, cutout: "65%",
            plugins: { legend: { position: "bottom" } },
        },
    });
}

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

function renderTtcDept(d) {
    const c = document.getElementById("chartTtcDept");
    new Chart(c, {
        type: "bar",
        data: { labels: d.labels, datasets: [{ label: "Среднее время, дней", data: d.avg, backgroundColor: HR.palette.coral, borderRadius: 6 }] },
        options: {
            responsive: true, maintainAspectRatio: false, scales: HR.baseScales,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => `${ctx.parsed.y} дн. (${d.count[ctx.dataIndex]} вакансий)` } },
            },
        },
    });
}

function renderTtcGrade(d) {
    const c = document.getElementById("chartTtcGrade");
    new Chart(c, {
        type: "line",
        data: {
            labels: d.labels,
            datasets: [{
                label: "Среднее время, дней", data: d.avg,
                borderColor: HR.palette.teal, backgroundColor: HR.gradient(c, HR.palette.teal),
                fill: true, tension: 0.4, pointRadius: 5, pointBackgroundColor: HR.palette.teal, borderWidth: 2.5,
            }],
        },
        options: { responsive: true, maintainAspectRatio: false, scales: HR.baseScales, plugins: { legend: { display: false } } },
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

function renderStackPop(d) {
    const c = document.getElementById("chartStackPop");
    new Chart(c, {
        type: "bar",
        data: { labels: d.labels, datasets: [{ label: "Сотрудники", data: d.data, backgroundColor: HR.palette.emerald, borderRadius: 4 }] },
        options: {
            indexAxis: "y", responsive: true, maintainAspectRatio: false,
            scales: { x: HR.baseScales.y, y: { ...HR.baseScales.x, grid: { display: false } } },
            plugins: { legend: { display: false } },
        },
    });
}

function renderVacStatus(d) {
    const c = document.getElementById("chartVacStatus");
    new Chart(c, {
        type: "doughnut",
        data: {
            labels: d.labels,
            datasets: [{ data: d.data, backgroundColor: [HR.palette.violet, HR.palette.emerald, "#94a3b8"], borderColor: HR.CARD_BG, borderWidth: 3, hoverOffset: 8 }],
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: "65%", plugins: { legend: { position: "bottom" } } },
    });
}
