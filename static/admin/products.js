document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(".categories").forEach(link => {
        link.onclick = ()=> {
            let selectedCategory = link.dataset.category;
            document.querySelectorAll(".category").forEach(div => {
                if (div.dataset.category === selectedCategory) {
                    div.style.display = "block";
                } else {
                    div.style.display = "none";
                }
            });
            return false;
        };
    });

    document.querySelector("#allcategories").onclick = () => {
        document.querySelectorAll(".category").forEach(div => {
            div.style.display = "block";
        });
        return false;
    };

    document.querySelectorAll(".productName").forEach(link => {
        link.onclick = ()=> {
            let name = link.dataset.name;
            const request = new XMLHttpRequest();
            request.open('GET', `/getinfo/${name}`);
            request.onload = () => {            
                let res = JSON.parse(request.responseText);
                if (res.success) {
                    let p = res.data;
                    let message = `Name: ${p.name}\nCatrgory: ${p.category}\nSubCategory: ${p.subcategory}\nPrice: Rs ${p.price} / ${p.unit}\nStock: ${p.stock}`;
                    alert(message);
                } else {
                    alert("Invalid Request");
                }
            };
            request.send();
            return false;
        };
    });
});