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
            alert("Product Added to Your Cart");
        } else {
            alert(res.message);
        }
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