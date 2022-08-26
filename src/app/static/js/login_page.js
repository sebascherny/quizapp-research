'use strict';
const e = React.createElement;

function App() {
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [message, setMessage] = React.useState("");

  const success = async (text) => {
    await localStorage.setItem("userToken", text.access);
    await localStorage.setItem("loggedInUsername", username);
    window.location = "/dashboard";
  };

  const checkIsEmpty = () => {
    if (!username) {
      setMessage("Username is required");
      return true;
    }
    if (!password) {
      setMessage("Password is required");
      return true;
    }
    return false;
  }

  const tryLogin = async (e) => {
    e.preventDefault();
    if (checkIsEmpty()) {
      return;
    }
    await login_api(username, password, success, (text) => { setMessage(text) });
  };

  const tryRegister = async (e) => {
    e.preventDefault();
    if (checkIsEmpty()) {
      return;
    }
    await register_api(username, password, success, (text) => { setMessage(text) });
  };

  if (localStorage.getItem("userToken") != null) {
    window.location = window.location.origin + "/dashboard";
  }

  return (
    <div style={{
      width: "400px", margin: "auto", marginTop: "200px",
      boxShadow: "5px 5px 20px #cccccccc",
      padding: "1em"
    }}>
      <form>
        <div className="mb-3">
          <label htmlFor="username" className="form-label">Username</label>
          <input autoFocus type="text" className="form-control" id="username" placeholder="username"
            onChange={(e) => { setUsername(e.target.value) }} value={username} />
        </div>
        <div className="mb-3">
          <label htmlFor="password" className="form-label">Password</label>
          <input type="password" className="form-control" id="password" placeholder="password"
            onChange={(e) => { setPassword(e.target.value) }} value={password} />
        </div>
        <div style={{ margin: "1em", color: "red" }}>{message}</div>
        <div style={{ margin: "1em" }}>
          <button type="submit" style={{ marginTop: "inherit" }} className="btn btn-primary" onClick={tryLogin}>Login</button>
          <button type="submit" style={{ marginLeft: "inherit", marginTop: "inherit" }} className="btn btn-primary" onClick={tryRegister}>Register</button>
        </div>
      </form>
    </div>
  );
}

const domContainer = document.querySelector('#reactAppContainer');
ReactDOM.render(
  e(App),
  domContainer
);

