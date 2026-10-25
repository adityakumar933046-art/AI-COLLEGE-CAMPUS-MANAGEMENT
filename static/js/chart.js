/* ===========================================
   SMART CAMPUS ERP REAL ACADEMIC CHARTS
=========================================== */

document.addEventListener("DOMContentLoaded", function () {
    fetch("/dashboard/api/analytics/")
        .then(response => {
            if (!response.ok) throw new Error("Analytics API returned error status");
            return response.json();
        })
        .then(apiData => {
            if (apiData.role === "ADMIN") {
                if (apiData.attendance) initLineChart("attendanceChart", "Overall Attendance %", apiData.attendance.labels, apiData.attendance.data, "rgba(37,99,235,.15)", "#2563eb");
                if (apiData.departments) initDoughnutChart("studentChart", apiData.departments.labels, apiData.departments.data);
                if (apiData.grades) initBarChart("gradeChart", "Grade Distribution", apiData.grades.labels, apiData.grades.data, "#22c55e");
                renderDefaultersTable(apiData.defaulters);
            } else if (apiData.role === "TEACHER") {
                if (apiData.courses) initBarChart("teacherAttendanceChart", "Course Attendance %", apiData.courses.labels, apiData.courses.data, "#2563eb");
            } else if (apiData.role === "STUDENT") {
                if (apiData.subjects) initBarChart("studentSubjectChart", "Subject Attendance %", apiData.subjects.labels, apiData.subjects.data, "#2563eb");
                if (apiData.sgpa_history) initLineChart("sgpaChart", "Semester SGPA History", apiData.sgpa_history.labels, apiData.sgpa_history.data, "rgba(34,197,94,.15)", "#22c55e", 10);
            }
        })
        .catch(err => {
            console.warn("Analytics API unavailable or empty data:", err);
        });
});

function initLineChart(canvasId, label, labels, data, bgColor, borderColor, maxVal = 100) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type: "line",
        data: {
            labels: labels && labels.length ? labels : ["No Data"],
            datasets: [{
                label: label,
                data: data && data.length ? data : [0],
                fill: true,
                borderWidth: 3,
                tension: .4,
                backgroundColor: bgColor,
                borderColor: borderColor
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true } },
            scales: { y: { beginAtZero: true, max: maxVal } }
        }
    });
}

function initBarChart(canvasId, label, labels, data, barColor) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels && labels.length ? labels : ["No Data"],
            datasets: [{
                label: label,
                data: data && data.length ? data : [0],
                backgroundColor: barColor,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

function initDoughnutChart(canvasId, labels, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: labels && labels.length ? labels : ["No Data"],
            datasets: [{
                data: data && data.length ? data : [0],
                backgroundColor: ["#2563eb", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function renderDefaultersTable(defaulters) {
    const container = document.getElementById("defaultersTableBody");
    if (!container) return;
    if (!defaulters || defaulters.length === 0) {
        container.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">No attendance defaulters (< 75%) identified.</td></tr>';
        return;
    }

    let html = "";
    defaulters.forEach(d => {
        html += `<tr>
            <td><strong>${d.name}</strong></td>
            <td><span class="badge bg-secondary">${d.roll_no}</span></td>
            <td>${d.department}</td>
            <td><span class="badge bg-danger">${d.attendance_pct}%</span></td>
        </tr>`;
    });
    container.innerHTML = html;
}
