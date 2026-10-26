/**
 * ChallengeHire - Dashboard & Analytics Visualizations
 * Provides Chart.js configurations for Student & Recruiter Dashboards.
 */

function renderRadarComparison(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: '#e2e8f0' },
                    grid: { color: '#f1f5f9' },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: { stepSize: 20, font: { size: 10 } }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, font: { weight: '600' } }
                }
            }
        }
    });
}

function renderDonutFunnel(canvasId, labels, dataCounts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: dataCounts,
                backgroundColor: ['#6366f1', '#f59e0b', '#0284c7', '#10b981', '#ef4444'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}
