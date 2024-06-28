// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

contract P2PLending {
    struct LoanRequest {
        uint id;
        string username;
        address walletAddress;
        uint amount;
        uint interestRate;
        uint duration; // in months
        string purpose;
        bool funded;
        uint startTime;
        uint monthlyPayment;
        uint remainingDebt;
        address lender; // New field to store lender's address
    }

    uint public nextRequestId;
    mapping(uint => LoanRequest) public loanRequests;

    event LoanRequestCreated(
        uint id,
        string username,
        address walletAddress,
        uint amount,
        uint interestRate,
        uint duration,
        string purpose
    );
    event LoanFunded(uint id, address lender, address walletAddress); // Updated event
    event LoanPartiallyRepaid(uint id, address payer, uint amount);

    function createLoanRequest(
        string memory _username,
        address _walletAddress,
        uint _amount,
        uint _interestRate,
        uint _duration,
        string memory _purpose
    ) external {
        require(_amount > 0, "Amount must be greater than zero");
        require(_interestRate > 0, "Interest rate must be greater than zero");
        require(_duration > 0, "Duration must be greater than zero");

        uint monthlyPayment = (_amount + (_amount * _interestRate / 100)) / _duration;

        loanRequests[nextRequestId] = LoanRequest({
            id: nextRequestId,
            username: _username,
            walletAddress: _walletAddress,
            amount: _amount,
            interestRate: _interestRate,
            duration: _duration,
            purpose: _purpose,
            funded: false,
            startTime: 0,
            monthlyPayment: monthlyPayment,
            remainingDebt: _amount,
            lender: address(0) // Initialize lender as zero address
        });

        emit LoanRequestCreated(nextRequestId, _username, _walletAddress, _amount, _interestRate, _duration, _purpose);
        nextRequestId++;
    }

    function fundLoan(uint _id) external payable {
        LoanRequest storage request = loanRequests[_id];
        require(!request.funded, "Loan already funded");
        require(msg.value == request.amount, "Incorrect amount");

        request.funded = true;
        request.startTime = block.timestamp;
        request.remainingDebt = request.amount;
        request.lender = msg.sender; // Record lender's address

        payable(request.walletAddress).transfer(request.amount);

        emit LoanFunded(_id, msg.sender, request.walletAddress); // Emit lender's address
    }

    function repayLoan(uint _id) external payable {
        LoanRequest storage request = loanRequests[_id];
        require(request.funded, "Loan not funded yet");
        require(block.timestamp < request.startTime + request.duration * 30 days, "Loan duration has ended");
        require(msg.value <= request.remainingDebt, "Cannot repay more than remaining debt");

        request.remainingDebt -= msg.value;

        emit LoanPartiallyRepaid(_id, msg.sender, msg.value);
    }

    function getLoanRequest(uint _id) external view returns (
        uint id,
        string memory username,
        address walletAddress,
        uint amount,
        uint interestRate,
        uint duration,
        string memory purpose,
        bool funded,
        uint startTime,
        uint monthlyPayment,
        uint remainingDebt,
        address lender
    ) {
        LoanRequest storage request = loanRequests[_id];
        return (
            request.id,
            request.username,
            request.walletAddress,
            request.amount,
            request.interestRate,
            request.duration,
            request.purpose,
            request.funded,
            request.startTime,
            request.monthlyPayment,
            request.remainingDebt,
            request.lender
        );
    }

    function getNumLoanRequests() external view returns (uint) {
        return nextRequestId;
    }
}
