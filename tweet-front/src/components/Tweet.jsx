export default function Tweet(props) {
  
  return (
    <div className="card shadow p-3 rounded" onClick={props.onClick}>
      <div className="tweet-content">
        <p><b>@{props.tweet.user}</b> ({props.tweet.full.user.id_str})</p>
        <p style={{color: "grey"}}>{new Date(props.tweet.full.created_at).toLocaleString()}</p>
        <p>{props.tweet.tweet}</p>
        <p><b>URLs:</b></p>
        <ul style={{fontStyle: "italic", listStyle: "none"}}>
          {props.tweet.full.urls.map(url => {
            return <li>{url}</li>
          })}
        </ul>
        {props.quantidade && 
        <>
          <p>Quantidade: <b>{props.quantidade}</b></p>
          <div className="d-flex justify-content-between">
            <div className="d-flex gap-2">
              <button className="btn btn-danger" onClick={() => props.downHandler(props.clusterId)}><i className="bi bi-hand-thumbs-down-fill"></i></button>
              <button className="btn btn-success" onClick={() => props.upHandler(props.clusterId)}><i className="bi bi-hand-thumbs-up-fill"></i></button>
            </div>
            <button className="btn btn-info" onClick={props.verTodosHandler}>Ver todos os tweets</button>
          </div>
        </>
        }
      </div>
    </div>
  )
}