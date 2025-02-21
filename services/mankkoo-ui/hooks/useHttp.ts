import { useEffect, useState } from 'react';
import axios from 'axios';
import withReactContent from 'sweetalert2-react-content';
import Swal from 'sweetalert2';

import { API_BASE } from '@/api/ApiUrl';

//todo introduce api path as array
//todo introduce query paramas as map
export function useGetHttp<Type>(apiPath: string, enabled: boolean=true): {isFetching: boolean, fetchedData?: Type, setFetchedData?: unknown, error?: string } {
  
    const [isFetching, setIsFetching] = useState<boolean>(false);
    const [error, setError] = useState<string>();
    const [fetchedData, setFetchedData] = useState<Type>();

    useEffect(() => {
        async function fetchData() {
            setIsFetching(true);
            try {
                const response = await axios.get<Type>(API_BASE + apiPath);
                setFetchedData(response.data);
            } catch (error) {
                let errorMessage = 'Failed to fetch data from ';
                
                if (error instanceof Error) {
                    errorMessage = error.message
                } 
                setError(errorMessage);
            }

            setIsFetching(false);
        }

        if (enabled) fetchData();
    }, [apiPath, enabled]);

    return {
        isFetching,
        fetchedData,
        setFetchedData,
        error
    }
}

const MySwal = withReactContent(Swal);

export function uploadFile(apiPath: string, file: File) {
    const data = new FormData();
    data.set('operations', file);

    axios.post(API_BASE + apiPath,
        data,
        { headers: {
            'Content-Type': 'multipart/form-data',
            'Content-Length': `${file.size}`,
        }} )
    .then(_ => {
        MySwal.fire({
            title: 'Success!',
            text: 'File uploaded correctly',
            icon: 'success',
            confirmButtonText: 'Cool'})
    })
    .catch(error => {
        console.error(error);
        MySwal.fire({
            title: 'Error!',
            text: 'There was a problem with file upload',
            icon: 'error',
            confirmButtonText: 'Ok'
        })
    });
}

