function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function demo() {
    while (true) {
        await sleep(1500)
        const uploadStatus = document.getElementById('upload-status');
    
        if (uploadStatus.value == 'success') {
            Swal.fire({
                title: 'Success!',
                text: 'File uploaded correctly',
                icon: 'success',
                confirmButtonText: 'Cool'
            })
        } 
        
        if (uploadStatus.value == 'failure') {
            Swal.fire({
                title: 'Error!',
                text: 'There was a problem with file upload',
                icon: 'error',
                confirmButtonText: 'Ok'
            })
        };
    
        uploadStatus.value = "no-info";
    }
}

console.log('Starting upload status script')

demo();