fetch("http://127.0.0.1:5000/api/analytics/overview")
    .then(res => res.json())
    .then(data => {
        document.getElementById("revenue").innerText = "₹ " + data.total_revenue;
        document.getElementById("investment").innerText = "₹ " + data.total_sponsor_investment;
        document.getElementById("profit").innerText = "₹ " + data.profit;

        const ctx = document.getElementById("financeChart");

        new Chart(ctx, {
            type: "bar",
            data: {
                labels: ["Budget", "Revenue", "Investment", "Profit"],
                datasets: [{
                    data: [
                        data.total_budget,
                        data.total_revenue,
                        data.total_sponsor_investment,
                        data.profit
                    ],
                    backgroundColor: [
                        "#1B2F4A",
                        "#11C5D9",
                        "#F5C16C",
                        "#21E6A2"
                    ]
                }]
            },
            options: {
                plugins: {
                    legend: { display: false }
                }
            }
        });
    });
