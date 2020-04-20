document.addEventListener('DOMContentLoaded', () => {
    document.querySelector("#cartdivision").style.display = "none";
    checkcart()

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

    document.querySelector("#erasecart").onclick = ()=> {
        const request = new XMLHttpRequest();
        request.open('GET', "/erasecart");
        request.onload = () => {
            let res = JSON.parse(request.responseText);
            if (res.success) {
                document.querySelector("#cart_table").innerHTML = '';
                document.querySelector("#cartdivision").style.display = "none";
            } else {
                alert(res.message);
            }
        };
        request.send();
        return false;
    };
});

function addToCart(pid) {
    var qty = document.getElementById(pid).value;
    if (!qty) {
        alert("type a quantity");
        return false;
    }
    add2cart(pid, qty);
    document.getElementById(pid).value = "";
    document.getElementById(pid).blur();
    return false;
}

function add2cart(pid, qty) {    
    const request = new XMLHttpRequest();
    request.open('GET', `/add2cart/${pid}/${qty}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            const template = Handlebars.compile(document.querySelector('#cart_row').innerHTML);
            document.querySelector("#cartdivision").style.display = "block";
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
                document.querySelector("#cartdivision").style.display = "none";
            } else {
                document.getElementById(name).remove();
                document.querySelector("#cartprice").innerHTML = res.amount;;
            }            
        } else {
            alert(res.message);
        }
    };
    request.send();
    return false;
}

function checkcart() {
    const request = new XMLHttpRequest();
    request.open('GET', "/ifcart");
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        let d = document.querySelector("#cartdivision");
        if (res.success)
            d.style.display = "block";
        else
            d.style.display = "none";
    };
    request.send();
}

function getProductInfo(name) {
    const request = new XMLHttpRequest();
    request.open('GET', `/productInfo/${name}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            alert(res.message);
        } else {
            alert(res.message);
        }
    };
    request.send();
    return false;
}