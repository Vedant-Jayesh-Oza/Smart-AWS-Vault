import { Auth } from 'aws-amplify';
import awsconfig from './aws-exports';

Auth.configure(awsconfig);

async function signIn(username, password) {
    try {
        const user = await Auth.signIn(username, password);
        console.log('User signed in:', user);
        return user;
    } catch (error) {
        console.error('Error signing in:', error);
        throw error;
    }
}

async function signOut() {
    try {
        await Auth.signOut();
        console.log('User signed out');
    } catch (error) {
        console.error('Error signing out:', error);
    }
}

async function checkAuth() {
    try {
        const user = await Auth.currentAuthenticatedUser();
        return user;
    } catch (error) {
        return null;
    }
}

export { signIn, signOut, checkAuth };
