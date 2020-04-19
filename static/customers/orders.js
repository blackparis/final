document.addEventListener('DOMContentLoaded', () => {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('order closed', data => {
        const request = new XMLHttpRequest();
        request.open('GET', `/getusername`);
        request.onload = () => {
            let res = JSON.parse(request.responseText);
            if (res.success && (data.username === res.username)) {
                updateCloseOrderNotification(data.orderid, data.username);
            }
        };
        request.send();
    });

    socket.on('order cancelled', data => {
        const request = new XMLHttpRequest();
        request.open('GET', `/getusername`);
        request.onload = () => {
            let res = JSON.parse(request.responseText);
            if (res.success && (data.username === res.username)) {
                updateCancelledOrderNotification(data.orderid, data.username);
            }
        };
        request.send();
    });    

    document.querySelectorAll(".statuslinks").forEach(a => {
        a.onclick = ()=> {
            let status = a.dataset.status;
            sortorders(status);
            return false;
        };
    });

    document.querySelector("#allorderslink").onclick = ()=> {
        document.querySelectorAll(".allorders").forEach(d => {
            d.style.display = "block";
        });
        return false;
    }

    document.querySelectorAll(".btn-danger").forEach(b => {
        b.onclick = ()=> {
            var r = confirm("Are You Sure?");
            if (r === true) {
                let orderid = b.dataset.orderid;
                b.disabled = true;
                let notifid = `notif_${orderid}`;
                document.getElementById(notifid).innerHTML = "Please Wait";
                
                const request = new XMLHttpRequest();
                request.open('GET', `/cancel/order/${orderid}`);
                request.onload = () => {
                    let res = JSON.parse(request.responseText);
                    if (res.success) {
                        document.getElementById(notifid).innerHTML = "";
                        let statusid = `status_${orderid}`;
                        document.getElementById(statusid).innerHTML = res.message;
                        document.getElementById(orderid).dataset.orderstatus = res.message;
                        let preferedid = `preferedTime_${orderid}`;
                        document.getElementById(preferedid).remove();
                        alert("Your request is under process.\nYou will be notified once your order is cancelled");
                    }                    
                    else {
                        alert(res.message);
                        location.reload();
                    }                    
                };
                request.send();
                return false;
            }
        };
    });
});

function sortorders(status) {
    document.querySelectorAll(".allorders").forEach(d => {
        if (d.dataset.orderstatus === status)
            d.style.display = "block";
        else
            d.style.display = "none";
    });
    return false;
}

function updateCloseOrderNotification(orderid, username) {
    const request = new XMLHttpRequest();
    request.open('GET', `/orderdetails/${username}/${orderid}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            document.getElementById(orderid).remove();
            var ordertemplate = Handlebars.compile(document.querySelector('#OrderTemplate').innerHTML);
            var template = ordertemplate(res.response);
            var orders = document.querySelector("#ordertemplate").innerHTML;
            template += orders;
            document.querySelector("#ordertemplate").innerHTML = template;
            let count = document.querySelector("#countOfClosedOrders").innerHTML;
            count++;
            document.querySelector("#countOfClosedOrders").innerHTML = count;
        }                    
    };
    request.send();
}

function updateCancelledOrderNotification(orderid, username) {
    const request = new XMLHttpRequest();
    request.open('GET', `/orderdetails/${username}/${orderid}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            document.getElementById(orderid).remove();
            var ordertemplate = Handlebars.compile(document.querySelector('#OrderTemplate').innerHTML);
            var template = ordertemplate(res.response);
            var orders = document.querySelector("#ordertemplate").innerHTML;
            template += orders;
            document.querySelector("#ordertemplate").innerHTML = template;
            let count = document.querySelector("#countOfCancelledOrders").innerHTML;
            count++;
            document.querySelector("#countOfCancelledOrders").innerHTML = count;
        }                    
    };
    request.send();
}