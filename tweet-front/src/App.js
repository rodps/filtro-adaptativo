import { useEffect, useState } from 'react';
import './App.css';
import Tweet from './components/Tweet';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {

  const [clusters, setClusters] = useState()
  const [clusterSelected, setClusterSelected] = useState()
  const [filterSelected, setFilterSelected] = useState('')
  const [filters, setFilters] = useState([])
  const [filterValue, setFilterValue] = useState('')

  useEffect(() => {
    setClusters()
    fetch('http://127.0.0.1:8000/tweets')
      .then(res => res.json())
      .then(data => { 
        const ordered = data.sort((a, b) => {
          return a.tweets.length > b.tweets.length ? -1 : 1
        })
        setClusters(ordered)
      })
  }, []);

  useEffect(() => {
    getFilters()
  }, [filterSelected])


  const getFilters = () => {
    fetch('http://127.0.0.1:8000/filters?type=' + filterSelected)
      .then(res => res.json())
      .then(data => setFilters(data))
  }

  const addFilter = () => {
    fetch('http://127.0.0.1:8000/filters', {
      method: 'POST',
      body: JSON.stringify({
        text: filterValue,
        type: filterSelected
      }),
      headers: {
        "Content-Type": "application/json",
      }
    })
      .then(() => {
        getFilters()
      })
  }

  const renderGroup = (group) => {
    return (
      group.map((t, i) => {
        return <Tweet tweet={t} key={i} />
      })
    )
  }

  const upHandler = (clusterId) => {
    fetch('http://127.0.0.1:8000/up/cluster/' + clusterId, { method: "POST" })
      .then(() => {
        setClusters(clusters.filter((c) => c.cluster_id !== clusterId ))
        toast("Tweet sinalizado com sucesso", {
          type: "success"
        })
      })
  }

  const downHandler = (clusterId) => {
    fetch('http://127.0.0.1:8000/down/cluster/' + clusterId, { method: "POST" })
      .then(() => {
        setClusters(clusters.filter((c) => c.cluster_id !== clusterId ))
        toast("Tweet sinalizado com sucesso", {
          type: "error"
        })
      })
  }

  if(clusterSelected !== undefined || clusterSelected != null) {
    return (
      <div className='container mt-5 mb-5'>
        <button onClick={() => setClusterSelected(undefined)} className='btn btn-primary mb-5'>Voltar</button>
        <div className='d-flex flex-column gap-3'>
          {renderGroup(clusterSelected.tweets)}
        </div>
      </div>
    )
  } else {
    return (
      <div className='container'>
        <div className='row p-5'>
          <div className='col-9'>
            <div className='d-flex flex-column gap-3'>
              <h1>Tweets</h1>
              {!clusters && <p>Carregando...</p>}
              {clusters && clusters.map((element, i) => {
                return <Tweet 
                        tweet={element.tweets[0]} 
                        clusterId={element.cluster_id}
                        verTodosHandler={() => setClusterSelected(element)}
                        upHandler={upHandler}
                        downHandler={downHandler} 
                        key={i} 
                        quantidade={element.tweets.length} />
              })}
            </div>
          </div>
          <div className='col-3'>
            <div className='position-fixed'>
              <h3 className='mb-4'>Filtros de bloqueio</h3>
              <div className="d-grid gap-2">
                <button className="btn btn-dark" type="button" data-bs-toggle="modal" data-bs-target="#exampleModal" onClick={() => setFilterSelected('keyword')}>Palavras-chave</button>
                <button className="btn btn-dark" type="button" data-bs-toggle="modal" data-bs-target="#exampleModal" onClick={() => setFilterSelected('url')}>URLs</button>
                <button className="btn btn-dark" type="button" data-bs-toggle="modal" data-bs-target="#exampleModal" onClick={() => setFilterSelected('user')}>Usuários</button>
              </div>
            </div>
          </div>
        </div>

        {/* <!-- Modal --> */}
        <div className="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h1 className="modal-title fs-5" id="exampleModalLabel">Palavras-chave</h1>
                <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div className="modal-body">
                <div className='d-flex gap-2 mb-3'>
                  <input className='form-control' placeholder='Adicionar palavra-chave' value={filterValue} onChange={e => setFilterValue(e.target.value)} />
                  <button className='btn btn-primary' onClick={addFilter}>Adicionar</button>
                </div>
                <ul>
                  {filters.map((filter, i) => {
                    return <li key={i}>{filter.text}</li>
                  })}
                </ul>
              </div>
            </div>
          </div>
        </div>

        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="colored"
          />

      </div>
    );
  }

}

export default App;
