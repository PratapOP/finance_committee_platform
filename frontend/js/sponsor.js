fetch("http://127.0.0.1:5000/api/sponsors/")
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById("sponsorList");

        data.forEach(s => {
            const div = document.createElement("div");
            div.className = "stat-card";
            div.innerHTML = `
                <h2>${s.name}</h2>
                <p>${s.industry}</p>
                <p>₹ ${s.total_invested}</p>
            `;
            container.appendChild(div);
        });
    });
