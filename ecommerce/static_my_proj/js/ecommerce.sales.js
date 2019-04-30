$(document).ready(function() {
    function renderChart(id, data, labels) {
        var ctx = $(`#${id}`);
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sales',
                    data: data,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
    }
    function getSalesData(id, type) {
        var url = "/analytics/api/sales/data/";
        var method = "GET";
        var data = {
            "type": type
        };
        $.ajax({
            url: url,
            method: method,
            data: data,
            success: function(data) {
                renderChart(id, data.data, data.labels);
            },
            error: function(errorData) {
                console.log(errorData);
                $.alert({
                    title: "Oops!",
                    content: "An error occurred",
                    theme: "modern"
                });
            }
        });
    }
    var chartToRender = $(".render-sales-chart");
    $.each(chartToRender, function(index, element) {
        var thisChart = $(this);
        if (thisChart.attr("id") && thisChart.attr("data-type")) {
            getSalesData(thisChart.attr("id"), thisChart.attr("data-type"));
        }
    });
});