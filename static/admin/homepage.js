document.addEventListener('DOMContentLoaded', () => {
    
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('new order', data => {
        let count1 = document.querySelector("#countOfOpenOrders").innerHTML;
        count1++;
        document.querySelector("#countOfOpenOrders").innerHTML = count1;
        newOrderNotification(data.code);
    });

    socket.on('order cancellation', data => {
        let count1 = document.querySelector("#countOfOpenOrders").innerHTML;
        count1--;
        document.querySelector("#countOfOpenOrders").innerHTML = count1;

        let count2 = document.querySelector("#ordersForCancellation").innerHTML;
        count2++;
        document.querySelector("#ordersForCancellation").innerHTML = count2;

        orderCancellationNotification(data.code);
    });    
});

function orderCancellationNotification(code) {
    const request = new XMLHttpRequest();
    request.open('GET', `/admin/orderdetails/${code}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            let oid = res.response.id;
            if (document.getElementById(oid)) {
                document.getElementById(oid).remove();
            }
            
            var ordertemplate = Handlebars.compile(document.querySelector('#newOrderTemplate').innerHTML);
            var template = ordertemplate(res.response);
            var orders = document.querySelector("#homepageorders").innerHTML;
            template += orders;
            document.querySelector("#homepageorders").innerHTML = template;
        }
        else {
            alert(res.message);
        }                    
    };
    request.send();
}

function newOrderNotification(code) {
    const request = new XMLHttpRequest();
    request.open('GET', `/admin/orderdetails/${code}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            var ordertemplate = Handlebars.compile(document.querySelector('#newOrderTemplate').innerHTML);
            var template = ordertemplate(res.response);
            var orders = document.querySelector("#homepageorders").innerHTML;
            template += orders;
            document.querySelector("#homepageorders").innerHTML = template;
        }
        else {
            alert(res.message);
        }                    
    };
    request.send();
}


function closeorder(orderid) {
    let closeOrderButtonid = `closeOrderButton_${orderid}`;
    let b = document.getElementById(closeOrderButtonid);
    b.disabled = true;
    let closenotifid = `closenotif_${orderid}`;
    document.getElementById(closenotifid).innerHTML = "Please Wait";

    const request = new XMLHttpRequest();
    request.open('GET', `/admin/closeorder/${orderid}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            document.getElementById(orderid).remove();
            let count = document.querySelector("#countOfOpenOrders").innerHTML;
            count--;
            document.querySelector("#countOfOpenOrders").innerHTML = count;
            alert("Order Marked as Dispatched");
        }                    
        else {
            alert(res.message);
            location.reload();
        }                    
    };
    request.send();
    return false;
}

function cancelorder(orderid) {
    var r = confirm("Are You Sure?");
    if (r === true) {
        var cancelOrderButtonid = `cancelOrderButton_${orderid}`;
        let b = document.getElementById(cancelOrderButtonid);
        b.disabled = true;
        let notifid = `cancelnotif_${orderid}`;
        document.getElementById(notifid).innerHTML = "Please Wait";
        
        const request = new XMLHttpRequest();
        request.open('GET', `/admin/cancelorder/${orderid}`);
        request.onload = () => {
            let res = JSON.parse(request.responseText);
            if (res.success) {
                document.getElementById(orderid).remove();
                let count = document.querySelector("#ordersForCancellation").innerHTML;
                count--;
                document.querySelector("#ordersForCancellation").innerHTML = count;
                alert("This Order is Cancelled");
            }                    
            else {
                alert(res.message);
                location.reload();
            }                    
        };
        request.send();
        return false;
    }
}