// Test script to verify role-based contacts functionality
const API_BASE = 'http://localhost:8000';

async function loginUser(email, password) {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
        throw new Error(`Login failed: ${response.status}`);
    }
    
    const data = await response.json();
    return data.access_token;
}

async function getParticipants(token) {
    const response = await fetch(`${API_BASE}/api/messages/participants`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
        throw new Error(`Get participants failed: ${response.status}`);
    }
    
    return await response.json();
}

async function testRoleBasedContacts() {
    console.log('Testing role-based contacts...\n');
    
    try {
        // Test Super Admin
        console.log('=== Testing Super Admin ===');
        const superAdminToken = await loginUser('admin@miraiworks.com', 'password');
        const superAdminParticipants = await getParticipants(superAdminToken);
        console.log('Super Admin can see:', superAdminParticipants.participants.length, 'participants');
        superAdminParticipants.participants.forEach(p => 
            console.log(`  - ${p.full_name} (${p.email}) from ${p.company_name || 'No company'}`)
        );
        
        console.log('\n=== Testing Company Admin ===');
        const companyAdminToken = await loginUser('admin@techcorp.com', 'password');
        const companyAdminParticipants = await getParticipants(companyAdminToken);
        console.log('Company Admin can see:', companyAdminParticipants.participants.length, 'participants');
        companyAdminParticipants.participants.forEach(p => 
            console.log(`  - ${p.full_name} (${p.email}) from ${p.company_name || 'No company'}`)
        );
        
    } catch (error) {
        console.error('Test failed:', error.message);
    }
}

testRoleBasedContacts();