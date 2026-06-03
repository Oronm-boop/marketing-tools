//前置
export const beforeEach = ()=>{
    console.log('前置');
    return true;
}

//后置
export const afterEach = ()=>{
    console.log('后置');
}