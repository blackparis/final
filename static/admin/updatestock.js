
function updatestock(pid) {
    let value = document.getElementById(pid).value;
    if (!value) {
        alert("Type a Value");
        return false;
    }
    const request = new XMLHttpRequest();
    request.open('POST', '/admin/stockupdate');
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            document.getElementById(res.name).remove();
            alert("Stock Updated");
        } else {
            document.getElementById(btnid).disabled = false;
            alert(res.message);
        }
    };
    const data = new FormData();
    data.append('pid', pid);
    data.append('value', value);
    request.send(data);
    let btnid = `btn_${pid}`;
    document.getElementById(btnid).disabled = true;
    return false;
}