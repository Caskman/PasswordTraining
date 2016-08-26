
var PasswordTrainingApp = React.createClass({
    getInitialState: function() {
        return {
            p1: 'password1', 
            p2: 'password2', 
            done: false,
            currentSessionId: -1,
            sessions: [],
        };
    },
    componentDidMount: function() {
        this.getSessionList();
    },
    getNextComparison: function(sessionId) {
        $.ajax({
            url: 'next/' + sessionId,
            dataType: 'json',
            type: 'GET',
            success: function(data) {
                if (data.id == -1) {
                    this.setState({done: true});
                } else {
                    this.setState({
                        password1: data.password1,
                        password2: data.password2,
                    });
                }
            }.bind(this),
            error: function(e) {
                console.error(e);
            }.bind(this),
        });
    },
    getSessionList: function() {
        $.ajax({
            url: 'sessions',
            dataType: 'json',
            type: 'GET',
            success: function(data) {
                this.setState({sessions: data});
                if (this.state.currentSessionId == -1 && data.length > 0) {
                    this.switchSession(data[0]);
                }
            }.bind(this),
            error: function(e) {
                console.error(e);
            }.bind(this),
        });
    },
    commitComparison: function(result) {
        $.ajax({
            url: 'next',
            dataType: 'json',
            type: 'POST',
            data: JSON.stringify({
                sessionId: this.state.currentSessionId,
                password1: this.state.password1,
                password2: this.state.password2,
                result: result,
            }),
            contentType: "application/json",
            success: function() {
                this.getNextComparison();
            }.bind(this),
            error: function(e) {
                console.error(e);
            }.bind(this),
        });
    },
    switchSession: function(sessionId) {
        if (this.state.currentSessionId != sessionId) {
            this.setState({currentSessionId: sessionId});
            this.getNextComparison(sessionId);
        }
    },
    createSession: function() {
        $.ajax({
            url: 'session',
            dataType: 'json',
            type: 'POST',
            success: function(sessionId) {
                this.switchSession(sessionId);
            }.bind(this),
            error: function(e) {
                console.error(e);
            }.bind(this),
        });
    },
    render: function() {
        // debugger;
        var self = this;
        var passwordContainerClassName = "password-container";
        var messageClassName = "message";
        if (self.state.done) {
            passwordContainerClassName += ' hidden';
        } else {
            messageClassName += ' hidden';
        }
        var sessionList = self.state.sessions.map(function(session, i) {
            return (
                <div className="session-item btn" key={i} onClick={self.switchSession.bind(self, session)}>
                    {session}
                </div>
            );
        });
        return (
            <div className="main-container">
                <div className="session-list">
                    {sessionList}
                    <div className="session-item btn" onClick={self.createSession}>
                        new session
                    </div>
                </div>
                <div className={passwordContainerClassName}>
                    <div className="first-pass">
                        <button className="btn" onClick={self.commitComparison.bind(self, -1)}>
                            {self.state.password1}
                        </button>
                    </div>
                    <div className="second-pass btn">
                        <button className="btn" onClick={self.commitComparison.bind(self, 1)}>
                            {self.state.password2}
                        </button>
                    </div>
                </div>
                <div className={messageClassName}>
                    Comparison Done!
                </div>
            </div>
        );
    },
});

ReactDOM.render(
    <PasswordTrainingApp/>,
    document.getElementById('content'),
);

