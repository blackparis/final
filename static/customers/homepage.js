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

    const cart_row_template = Handlebars.compile(document.querySelector('#cart_row').innerHTML);
    document.querySelectorAll(".cart").forEach(item => {
        item.onsubmit = ()=> {
            let pid = item.dataset.product_id;
            let qty = document.getElementById(pid).value;
            add2cart(pid, qty, cart_row_template);
            document.getElementById(pid).value = "";
            return false;
        };
    });

    document.querySelectorAll(".removeFromCart").forEach(a => {
        a.onclick = ()=> {
            let name = a.dataset.name;
            removeFromCart(name);
            return false;
        };
    });

    document.querySelector("#erasecart").onclick = ()=> {
        const request = new XMLHttpRequest();
        request.open('GET', "/erasecart");
        request.onload = () => {
            let res = JSON.parse(request.responseText);
            if (res.success) {
                document.querySelector("#cart_table").innerHTML = '';
            } else {
                alert(res.message);
            }
        };
        request.send();
        return false;
    };
});


function add2cart(pid, qty, template) {
    const request = new XMLHttpRequest();
    request.open('GET', `/add2cart/${pid}/${qty}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            let cart_row = template({'items': res.cart, 'amount': res.amount});
            document.querySelector("#cart_table").innerHTML = cart_row;
        } else {
            alert(res.message);
        }
    };
    request.send();
}

function removeFromCart(name) {
    const request = new XMLHttpRequest();
    request.open('GET', `/cart/remove/${name}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            if (res.amount === 0) {
                document.querySelector("#cart_table").innerHTML = '';
            } else {
                document.getElementById(name).remove();
                document.querySelector("#cartprice").innerHTML = res.amount;;
            }            
        } else {
            alert(res.message);
        }
    };
    request.send();
}