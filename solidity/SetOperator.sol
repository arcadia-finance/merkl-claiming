pragma solidity 0.8.22;

contract SetOperator {
    address public constant distributor = 0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae;
    address public constant operator = 0x3146e7bCeE81aE5a9BDcC8452ba7bBf9f8524205;


    function setOperatorMulti(address[] calldata users) external {
        for (uint i = 0; i < users.length; i++) {
            distributor.delegatecall(abi.encodeWithSignature("toggleOperator(address,address)", users[i], operator));
        }
    }
}