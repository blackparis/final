document.addEventListener('DOMContentLoaded', () => {

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
                let notifid = `cancelnotif_${orderid}`;
                document.getElementById(notifid).innerHTML = "Please Wait";
                
                const request = new XMLHttpRequest();
                request.open('GET', `/admin/cancelorder/${orderid}`);
                request.onload = () => {
                    let res = JSON.parse(request.responseText);
                    if (res.success) {
                        alert("This Order is Cancelled");
                        location.reload();
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