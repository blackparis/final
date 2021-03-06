document.addEventListener('DOMContentLoaded', () => {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('new order', data => {
        newOrderNotification(data.code);        
    });

    socket.on('order cancellation', data => {
        orderCancellationNotification(data.code);
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

    document.querySelectorAll(".btn-success").forEach(b => {
        b.onclick = ()=> {
            let orderid = b.dataset.orderid;
            b.disabled = true;
            let closenotifid = `closenotif_${orderid}`;
            document.getElementById(closenotifid).innerHTML = "Please Wait";

            const request = new XMLHttpRequest();
            request.open('GET', `/admin/closeorder/${orderid}`);
            request.onload = () => {
                let res = JSON.parse(request.responseText);
                if (res.success) {
                    document.getElementById(orderid).dataset.orderstatus = res.status;
                    document.getElementById(closenotifid).innerHTML = "";
                    let trlinks = `trlinks_${orderid}`;
                    document.getElementById(trlinks).remove();
                    let statusid = `status_${orderid}`;
                    document.getElementById(statusid).innerHTML = res.status;
                    let cid = `dispatch_${orderid}`;
                    document.getElementById(cid).innerHTML = `Dispatch Time: ${res.delivery_time}`;
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
        };
    });

    document.querySelectorAll(".btn-danger").forEach(b => {
        b.onclick = ()=> {
            var r = confirm("Are You Sure?");
            if (r === true) {
                let orderid = b.dataset.orderid;
                b.disabled = true;
                let notifid = `cancelnotif_${orderid}`;
                document.getElementById(notifid).innerHTML = "Please Wait";
                
                const request = new XMLHttpRequest();
                request.open('GET', `/admin/cancelorder/${orderid}`);
                request.onload = () => {
                    let res = JSON.parse(request.responseText);
                    if (res.success) {
                        let statusid = `status_${orderid}`;
                        document.getElementById(statusid).innerHTML = res.status;
                        let cid = `cancellation_${orderid}`;
                        document.getElementById(cid).innerHTML = `Time of Cancellation: ${res.cancellation_time}`;
                        document.getElementById(orderid).dataset.orderstatus = res.status;
                        let trlinks = `trlinks_${orderid}`;
                        document.getElementById(trlinks).remove();
                        let count = document.querySelector("#countOfCancelletionRequests").innerHTML;
                        count--;
                        document.querySelector("#countOfCancelletionRequests").innerHTML = count;
                        let prefered = `prefered_${orderid}`;
                        document.getElementById(prefered).remove();
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

function newOrderNotification(code) {
    const request = new XMLHttpRequest();
    request.open('GET', `/admin/orderdetails/${code}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            var ordertemplate = Handlebars.compile(document.querySelector('#newOrderTemplate').innerHTML);
            var template = ordertemplate(res.response);
            var orders = document.querySelector("#orderTemplateDiv").innerHTML;
            template += orders;
            document.querySelector("#orderTemplateDiv").innerHTML = template;
            let count = document.querySelector("#countOfOpenOrders").innerHTML;
            count++;
            document.querySelector("#countOfOpenOrders").innerHTML = count;
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
    //let orderid = b.dataset.orderid;
    b.disabled = true;
    let closenotifid = `closenotif_${orderid}`;
    document.getElementById(closenotifid).innerHTML = "Please Wait";

    const request = new XMLHttpRequest();
    request.open('GET', `/admin/closeorder/${orderid}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            document.getElementById(orderid).dataset.orderstatus = res.status;
            document.getElementById(closenotifid).innerHTML = "";
            let trlinks = `trlinks_${orderid}`;
            document.getElementById(trlinks).remove();
            let statusid = `status_${orderid}`;
            document.getElementById(statusid).innerHTML = res.status;
            let cid = `dispatch_${orderid}`;
            document.getElementById(cid).innerHTML = `Dispatch Time: ${res.delivery_time}`;
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
}

function orderCancellationNotification(code) {
    const request = new XMLHttpRequest();
    request.open('GET', `/admin/orderdetails/${code}`);
    request.onload = () => {
        let res = JSON.parse(request.responseText);
        if (res.success) {
            let oid = res.response.id;
            document.getElementById(oid).remove();
            var ordertemplate = Handlebars.compile(document.querySelector('#newOrderTemplate').innerHTML);
            var template = ordertemplate(res.response);
            var orders = document.querySelector("#orderTemplateDiv").innerHTML;
            template += orders;
            document.querySelector("#orderTemplateDiv").innerHTML = template;
            let count = document.querySelector("#countOfOpenOrders").innerHTML;
            count--;
            document.querySelector("#countOfOpenOrders").innerHTML = count;
            let cnt = document.querySelector("#countOfCancelletionRequests").innerHTML;
            cnt++;
            document.querySelector("#countOfCancelletionRequests").innerHTML = cnt;
        }                    
        else {
            alert(res.message);
        }                    
    };
    request.send();
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
                let statusid = `status_${orderid}`;
                document.getElementById(statusid).innerHTML = res.status;
                let cid = `cancellation_${orderid}`;
                document.getElementById(cid).innerHTML = `Time of Cancellation: ${res.cancellation_time}`;
                document.getElementById(orderid).dataset.orderstatus = res.status;
                let trlinks = `trlinks_${orderid}`;
                document.getElementById(trlinks).remove();
                let count = document.querySelector("#countOfCancelletionRequests").innerHTML;
                count--;
                document.querySelector("#countOfCancelletionRequests").innerHTML = count;
                let prefered = `prefered_${orderid}`;
                document.getElementById(prefered).remove();
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