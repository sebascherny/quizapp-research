'use strict';

class AppHeader extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const logout = async (e) => {
            await localStorage.removeItem("userToken");
            await localStorage.removeItem("loggedInUsername");
            this.props.setLoggedInUsername(null);
            if (this.props.redirectWhenLoggedOut) {
                window.location = "/login";
            }
        };
        if (this.props.loggedInUsername == null) {
            return <div style={{
                display: "flex", flexDirection: "row",
                maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
                padding: "1em"
            }} className="shadow">
                <a className="btn btn-light" style={{ marginLeft: "auto" }} href={window.location.origin + "/login"}>Login</a>
            </div>
        }
        return <div style={{
            display: "flex", flexDirection: "row",
            maxWidth: "800px", margin: "auto", marginTop: "1em", marginBottom: "1em",
            padding: "1em"
        }} className="shadow">
            <a className="btn btn-light shadow" onClick={() => { window.location = "/dashboard" }}>My dashboard</a>
            <a className="btn btn-light" style={{ marginLeft: "auto" }} onClick={logout}>Logout ({this.props.loggedInUsername})</a>
        </div>;
    }
}