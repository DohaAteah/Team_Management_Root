console.log('Hi')


$.ajax({
    type: 'GET',
    url: '/Tasks_Json/',
    succcess: function(response){
        console.log(response)  
       /* const data = response.data
        data.map(Task=>{
           print(Task.id)
        })*/
    },
    error: function(error){
        console.log(error)
    }
})

console.log('Hi2')


