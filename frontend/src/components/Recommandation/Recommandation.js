import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

// Recommandation component
const Recommandation = ({ incorrectCode, correctedCode, filename, language = 'javascript' }) => {
  return (
    <Box sx={{ my: 4 }}>
      <Typography variant="h6" sx={{ mb: 2, color: '#d32f2f', fontWeight: 700 }}>
        Incorrect Code
      </Typography>
      <Paper sx={{ background: '#fff0f0', p: 2, mb: 2, borderLeft: '5px solid #d32f2f' }}>
        <pre style={{ margin: 0, color: '#b71c1c' }}>
          <code>
            {incorrectCode}
          </code>
        </pre>
      </Paper>
      <Typography variant="subtitle1" sx={{ mb: 1, color: '#388e3c', fontWeight: 600 }}>
        Corrected Version ({filename})
      </Typography>
      <Paper sx={{ background: '#f1fff0', p: 2, borderLeft: '5px solid #388e3c' }}>
        <pre style={{ margin: 0, color: '#1b5e20' }}>
          <code>
            {correctedCode}
          </code>
        </pre>
      </Paper>
    </Box>
  );
};

// Example usage inside the same file
const incorrectCode = `import React from 'react'

function UserList(props) {
  const [users, setUsers] = React.useState([])
  
  React.useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(data => setUsers(data))
      .catch(error => console.log(error))
  }, [])

  return (
    <div>
      <h2>User List</h2>
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  )
// Missing closing parenthesis for function and missing semicolons
`;

const correctedCode = `import React from 'react';

function UserList(props) {
  const [users, setUsers] = React.useState([]);

  React.useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(data => setUsers(data))
      .catch(error => console.log(error));
  }, []);

  return (
    <div>
      <h2>User List</h2>
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default UserList;
`;

export const RecommandationExample = () => (
  <div>
    <Recommandation
      incorrectCode={incorrectCode}
      correctedCode={correctedCode}
      filename="utils.js"
      language="javascript"
    />
  </div>
);

export default Recommandation;